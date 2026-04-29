import base64
import json
import os
from typing import Dict
from typing import List
from typing import Optional

from utils import utils
from utils.debug import logger
from mcpconfig.config import mcp
from constants import constants
from mcptypes import assessment_config_tool_types as vo
from fastmcp import Context

def _get_control_map() -> Dict[str, List[str]]:
    value = os.getenv("CONTROL_MCP", "")
    if not value:
        return {}

    try:
        return json.loads(base64.b64decode(value).decode("utf-8"))
    except Exception as e:
        logger.error("CONTROL_MCP parse error: %s\n", e)
        return {}

def _filter_controls(controls: Optional[List[vo.ControlVO]], child_numbers: Optional[List[str]] = None) -> Optional[List[vo.ControlVO]]:
    if not controls:
        return None

    if not child_numbers:
        return controls

    allowed = set(child_numbers)
    filtered_controls: List[vo.ControlVO] = []

    for control in controls:
        if control.displayable in allowed:
            filtered_controls.append(control)
            continue

        filtered_children = _filter_controls(control.controls, child_numbers)
        if filtered_children:
            filtered_controls.append(control.model_copy(update={"controls": filtered_children}))

    return filtered_controls or None


def _filter_parent_controls(controls: Optional[List[vo.ControlVO]], control_map: Optional[Dict[str, List[str]]]) -> Optional[List[vo.ControlVO]]:
    if not controls or not control_map:
        return controls

    filtered_controls: List[vo.ControlVO] = []

    for control in controls:
        if not control.displayable or control.displayable not in control_map:
            continue

        child_numbers = control_map[control.displayable]
        if not child_numbers:
            filtered_controls.append(control)
            continue

        filtered_controls.append(
            control.model_copy(update={"controls": _filter_controls(control.controls, child_numbers)})
        )

    return filtered_controls


@mcp.tool()
async def get_default_ccf_assessment(ctx: Context | None = None) -> vo.AssessmentVO:
    """
        Get the default ccf assessment from CCow.
    """
    try:
        control_map = _get_control_map()
        logger.info("get_default_ccf_assessment: controlMap=%s\n", control_map)

        output=await utils.make_API_call_to_CCow({},constants.URL_PLANS+"/fetch-ccf-assessment", ctx=ctx)
        
        if isinstance(output, str) or  "error" in output:
            logger.error("get_default_ccf_assessment error: {}\n".format(output))
            return vo.AssessmentVO(error="Facing internal error")
    
        logger.debug("raw assessment output: {}\n".format(output))

        assessment=vo.AssessmentVO(**output)

        logger.debug("assessment output: {}\n".format(assessment))
        assessment.controls = _filter_parent_controls(assessment.controls, control_map)

        logger.debug("assessment output filtered: {}\n".format(assessment))
        return assessment
    except Exception as e:
        logger.error("get_default_ccf_assessment error: {}\n".format(e))
        return vo.AssessmentVO(error="Facing internal error")
    

@mcp.tool()
async def get_ccf_control_last_run_date(ccfControlIDs: List[str], ctx: Context | None = None) -> vo.ControlsLastRunDate:
    """
        Get the ccf assessment controls last run date. 
        
        input:
        ccfControlIDs: id (GUID) field of leaf controls in ccf assessment
    """
    try:
        logger.info("get_ccf_control_last_run_date: {} \n".format(ccfControlIDs))

        output=await utils.make_API_call_to_CCow({"ControlIDs": ccfControlIDs},constants.URL_PLAN_INSTANCE_CONTROLS+"/fetch-latest-run-date", ctx=ctx)
        
        if isinstance(output, str) or  "error" in output:
            logger.error("get_ccf_control_last_run_date error: {}\n".format(output))
            return vo.ControlsLastRunDate(error="Facing internal error")
    
        assessment=vo.ControlsLastRunDate(**output)
        logger.debug("last run date: {}\n".format(output))
        return assessment
    except Exception as e:
        logger.error("get_ccf_control_last_run_date error: {}\n".format(e))
        return vo.ControlsLastRunDate(error="Facing internal error")

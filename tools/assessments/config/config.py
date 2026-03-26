from typing import List
from typing import Tuple

from utils import utils
from utils.debug import logger
from mcpconfig.config import mcp
from constants import constants
from mcptypes import assessment_config_tool_types as vo
from fastmcp import Context

@mcp.tool(annotations=utils.tool_annotations("List All Assessment Categories",read_only=True))
async def list_all_assessment_categories(ctx: Context | None = None) -> vo.CategoryListVO:
    """
        Get all assessment categories
        
        Returns:
            - categories (List[Category]): A list of category objects, where each category includes:
                - id (str): Unique identifier of the assessment category.
                - name (str): Name of the category.
            - error (Optional[str]): An error message if any issues occurred during retrieval.

    """
    try:
        logger.info("get_all_assessment_categories: \n")

        output=await utils.make_API_call_to_CCow_and_get_response(constants.URL_ASSESSMENT_CATEGORIES, "GET", ctx=ctx)
        
        error = utils.build_structured_error(output, "assessments:list_all_assessment_categories")
        if error:
            logger.error("list_all_assessment_categories error: {}\n".format(output))
            return vo.CategoryListVO(error=error)
        
        # if isinstance(output, str):
        #     return output

        category_list: List[vo.CategoryVO] = []
        for item in output:
            if "name" in item:
                category_list.append(vo.CategoryVO(id=item["id"],name=item["name"]))
        
        logger.debug("categories: {}\n".format(category_list))
        return vo.CategoryListVO(categories=category_list)
    except Exception as e:
        logger.error("list_all_assessment_categories error: {}\n".format(e))
        return vo.CategoryListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "assessments:list_all_assessment_categories"))

@mcp.tool(annotations=utils.tool_annotations("List Assessments",read_only=True))
async def list_assessments(categoryId: str = "", categoryName: str = "", assessmentName: str = "", ctx: Context | None = None) -> vo.AssessmentListVO:
    """
        Get all assessments
        Args:
        categoryId: assessment category id (Optional)
        categoryName: assessment category name (Optional)
        assessmentName: assessment name (Optional)
        Returns:
            - assessments (List[Assessments]): A list of assessments objects, where each assessment includes:
                - id (str): Unique identifier of the assessment.
                - name (str): Name of the assessment.
                - category_name (str): Name of the category.
            - error (Optional[str]): An error message if any issues occurred during retrieval.
    """
    try:
        logger.info("get_all_assessments: \n")

        logger.debug("payload: {} {}\n".format(categoryId, categoryName))

        output=await utils.make_API_call_to_CCow_and_get_response(constants.URL_PLANS, "GET", {
            "fields": "basic",
            "category_id": categoryId,
            "category_name_contains": categoryName,
            "name_contains": assessmentName,
        }, ctx=ctx)
        error = utils.build_structured_error(output, "assessments:list_assessments")
        if error:
            logger.error("list_assessments error: {}\n".format(output))
            return vo.AssessmentListVO(error=error)
                    
        assessments: List[vo.AssessmentVO]=[]
        for item in output["items"]:
            if "name" in item and "categoryName" in item:
                assessments.append(vo.AssessmentVO(id=item["id"],name=item["name"],category_name=item["categoryName"]))
        
        logger.debug("assessments: {}\n".format(assessments))

        return vo.AssessmentListVO(assessments=assessments)
    except Exception as e:
        logger.error("list_assessments error: {}\n".format(e))
        return vo.AssessmentListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "assessments:list_assessments"))

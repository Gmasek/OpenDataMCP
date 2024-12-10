"""
Template for MCP server definitions.

This template provides a standardized structure for creating MCP server modules.
Each module should follow this pattern to ensure consistency across the codebase.

Module Structure:
1. Imports and Configuration
2. Global Constants
3. Registration Variables
4. Endpoint Sections (one per endpoint):
   - Pydantic Models (Input/Output)
   - Data Fetching Function
   - Handler Function
   - Tool Registration

Usage:
    Copy this template and replace the placeholders with actual implementation.
"""

# 1. Standard Imports Section
import logging
from typing import Any, List, Optional, Sequence

import httpx
import mcp.types as types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Initialize logging
log = logging.getLogger(__name__)
load_dotenv()

# 2. Constants Section
BASE_URL = "https://api.apollo.io/api/v1/mixed_people/search"
headers = {
    "accept": "application/json",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "x-api-key": os.getenv("personal_api_key"),
}
# 3. Registration Variables
RESOURCES: List[Any] = []  # resources that will be registered by each endpoints
RESOURCES_HANDLERS: dict[
    str, Any
] = {}  # resources handlers that will be registered by each endpoints
TOOLS: List[types.Tool] = []  # tools that will be registered by each endpoints
TOOLS_HANDLERS: dict[
    str, Any
] = {}  # tools handlers that will be registered by each endpoints

###################
# [Endpoint Name]
###################


# 1. Input/Output Models
class EndpointParams(BaseModel):
    """Input parameters for the endpoint."""

    person_titles: Optional[List[str]] = Field(
        None, description="Job titles held by the people you want to find."
    )
    person_locations: Optional[List[str]] = Field(
        None, description="Locations where the people live."
    )
    person_seniorities: Optional[List[str]] = Field(
        None, description="Job seniorities for the people."
    )
    organization_locations: Optional[List[str]] = Field(
        None, description="Headquarters locations of the person's current employer."
    )
    q_organization_domains: Optional[List[str]] = Field(
        None, description="Domain names of the person's employer."
    )
    contact_email_status: Optional[List[str]] = Field(
        None, description="Statuses of email addresses for the people."
    )
    organization_ids: Optional[List[str]] = Field(
        None, description="Apollo IDs for the companies (employers)."
    )
    organization_num_employees_ranges: Optional[List[str]] = Field(
        None, description="Ranges of employee numbers in the person's current company."
    )
    q_keywords: Optional[str] = Field(
        None, description="Keywords to filter the search results."
    )
    page: Optional[int] = Field(1, description="Page number of the results.")
    per_page: Optional[int] = Field(None, description="Number of results per page.")


class OrganizationEntry(BaseModel):
    created_at: Optional[str] = Field(
        None, description="Timestamp when the entry was created"
    )
    current: Optional[bool] = Field(
        None, description="Indicates if the position is current"
    )
    degree: Optional[str] = Field(
        None, description="Degree associated with the position, if applicable"
    )
    description: Optional[str] = Field(None, description="Description of the position")
    emails: Optional[str] = Field(
        None, description="Emails associated with the position"
    )
    end_date: Optional[str] = Field(None, description="End date of the position")
    grade_level: Optional[str] = Field(None, description="Grade level, if applicable")
    kind: Optional[str] = Field(None, description="Kind or type of position")
    major: Optional[str] = Field(
        None, description="Major field of study, if applicable"
    )
    organization_name: Optional[str] = Field(
        None, description="Name of the associated organization"
    )
    start_date: Optional[str] = Field(None, description="Start date of the position")
    title: Optional[str] = Field(None, description="Title held in the position")
    updated_at: Optional[str] = Field(
        None, description="Timestamp when the entry was last updated"
    )


class ContactEmail(BaseModel):
    email: Optional[str] = Field(None, description="Email address of the contact")
    email_status: Optional[str] = Field(
        None, description="Verification status of the email"
    )


class PhoneNumbers(BaseModel):
    sanitized_number: Optional[str] = Field(None, description="Sanitized phone number")
    status: Optional[str] = Field(
        None, description="Verification status of the phone number"
    )


class Contact(BaseModel):
    name: Optional[str] = Field(None, description="Name of the contact")
    linkedin_url: Optional[str] = Field(
        None, description="LinkedIn profile URL of the contact"
    )
    organization_name: Optional[str] = Field(
        None, description="Organization name of the contact"
    )
    email: Optional[str] = Field(None, description="Email address of the contact")
    email_true_status: Optional[str] = Field(
        None, description="Email verification status of the contact"
    )
    contact_emails: Optional[List[ContactEmail]] = Field(
        None, description="Emails associated with the contact"
    )


class TechnologyItem(BaseModel):
    uid: Optional[str] = Field(None, description="Unique ID of the technology")
    name: Optional[str] = Field(None, description="Name of the technology")
    category: Optional[str] = Field(None, description="Category of the technology")


class Organization(BaseModel):
    name: Optional[str] = Field(None, description="Name of the organization")
    website_url: Optional[str] = Field(
        None, description="Website URL of the organization"
    )
    linkedin_url: Optional[str] = Field(
        None, description="LinkedIn profile URL of the organization"
    )
    keywords: Optional[list[str]] = Field(
        None, description="Keywords associated with the organization"
    )
    estimated_num_employees: Optional[int] = Field(
        None, description="Estimated number of employees"
    )
    city: Optional[str] = Field(None, description="City of the organization")
    state: Optional[str] = Field(None, description="State of the organization")
    country: Optional[str] = Field(None, description="Country of the organization")
    annual_revenue: Optional[int] = Field(
        None, description="Annual revenue of the organization"
    )
    technology_names: Optional[list[str]] = Field(
        None, description="List of technology names associated with the organization"
    )
    current_technologies: Optional[list[TechnologyItem]] = Field(
        None,
        description="List of current technologies associated with the organization",
    )


class EndpointResult(BaseModel):
    """Single result item from the endpoint."""

    id: Optional[str] = Field(None, description="Unique identifier for the person")
    first_name: Optional[str] = Field(None, description="First name of the person")
    last_name: Optional[str] = Field(None, description="Last name of the person")
    name: Optional[str] = Field(None, description="Full name of the person")
    linkedin_url: Optional[str] = Field(
        None, description="LinkedIn profile URL of the person"
    )
    title: Optional[str] = Field(None, description="Current title of the person")
    email_status: Optional[str] = Field(
        None, description="Verification status of the email"
    )
    extrapolated_email_confidence: Optional[float] = Field(
        None, description="Confidence score for extrapolated email, if applicable"
    )
    headline: Optional[str] = Field(
        None, description="Headline of the person (e.g., current position)"
    )
    email: Optional[str] = Field(None, description="Email address of the person")
    employment_history: Optional[List[OrganizationEntry]] = Field(
        None, description="Employment history of the person"
    )
    state: Optional[str] = Field(None, description="State of the person")
    city: Optional[str] = Field(None, description="City of the person")
    country: Optional[str] = Field(None, description="Country of the person")
    contact: Optional[Contact] = Field(None, description="contact information")
    organization: Optional[Organization] = Field(
        None, description="Organization information"
    )
    seniority: Optional[str] = Field(None, description="Seniority level of the person")


class EndpointResponse(BaseModel):
    """Complete response from the endpoint."""

    people: Optional[List[EndpointResult]] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_endpoint_data(params: EndpointParams) -> EndpointResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}"

    params_dict = params.model_dump(exclude_none=True)

    # Construct the query string
    query_string = ""
    for key, value in params_dict.items():
        if isinstance(value, list):  # Handle list parameters
            for item in value:
                query_string += f"{key}[]={item.replace(' ', '%20')}&"
        else:  # Handle single-value parameters
            query_string += f"{key}={str(value).replace(' ', '%20')}&"

    # Finalize the endpoint URL
    if query_string:
        endpoint += "?" + query_string.rstrip("&")
    response = httpx.post(endpoint, headers=headers)
    response.raise_for_status()
    return EndpointResponse(**response.json())


# 3. Handler Function
async def handle_endpoint(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle the tool execution for this endpoint.

    Args:
        arguments: Dictionary of tool arguments

    Returns:
        Sequence of content objects

    Raises:
        Exception: If the handling fails
    """
    try:
        response = fetch_endpoint_data(EndpointParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="endpoint-name",
        description="Description of what this endpoint does",
        inputSchema=EndpointParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["endpoint-name"] = handle_endpoint


###################
# [Another Endpoint Name]
###################
...

# Server initialization (if module is run directly)
if __name__ == "__main__":
    # import anyio
    #
    # from odmcp.utils import run_server
    #
    # anyio.run(
    #    run_server, "service.name", RESOURCES, RESOURCES_HANDLERS, TOOLS, TOOLS_HANDLERS
    # )
    print(
        fetch_endpoint_data(
            EndpointParams(
                person_titles=["software engineer", "marketing manager"],
                person_locations=["california", "ireland"],
                person_seniorities=["senior"],
                contact_email_status=["verified", "unverified", "likely to engage"],
                per_page=1,
            )
        )
    )  # type: ignore

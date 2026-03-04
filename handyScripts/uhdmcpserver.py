
import json
import requests
import asyncio

from fastmcp import FastMCP

mcp = FastMCP("UHD MCP 🚀")


#UHD IP Address
#UHD_IP = "10.36.78.169"
@mcp.tool()
async def set_uhd_config(uhdIP: str, req: str):
    """
    Set the UHD configuration
    Args:
        uhdIP: The IP address of the UHD
        req: The JSON request body
    Returns:
        A dictionary containing the message, status code, and error if the request fails
    """
    url = f"http://{uhdIP}:80/connect/api/v1/config"
    json_d = json.loads(req)

    try:
        response = requests.post(url, json=json_d, verify=False)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return {"message": "Configuration has been set", "status_code": response.status_code}
    except requests.RequestException as e:
        return {"message": "Request failed", "status_code": 500, "error": str(e)}
  

@mcp.tool()
async def get_uhd_config(uhdIP: str):
    """
    Get the UHD configuration
    Args:
        uhdIP: The IP address of the UHD
    Returns:
        A dictionary containing the message, status code, and configuration if the request fails
    """
    url = f"http://{uhdIP}:80/connect/api/v1/config"

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return {"message": "Configuration fetched", "status_code": response.status_code, "configuration": response.json()}
    except requests.RequestException as e:
        return {"message": "Request failed", "status_code": 500, "error": str(e)}


@mcp.tool()
async def get_uhd_metrics(uhdIP: str):
    """
    Get the UHD metrics
    Args:
        uhdIP: The IP address of the UHD
    Returns:
        A dictionary containing the message, status code, and metrics if the request fails
    """
    url = f"http://{uhdIP}:80/connect/api/v1/metrics/operations/query"
    try:
        """Need to make this customizable"""
        a = {"port_metrics":{}}
        response = requests.post(url, json=a, verify=False)

        # Check if the request was successful (status code 200)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return response.json()
    except requests.RequestException as e:
        return {"message": "Request failed", "status_code": 500, "error": str(e)}


@mcp.tool()
async def clear_uhd_metrics(uhdIP: str):
    """
    Clear the UHD metrics
    Args:
        uhdIP: The IP address of the UHD
    Returns:
        A dictionary containing the message, status code, and error if the request fails
    """
    url = f"http://{uhdIP}:80/connect/api/v1/metrics/operations/clear"

    try:
        response = requests.post(url, verify=False)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return {"message": "Metrics have been cleared", "status_code": response.status_code}
    except requests.RequestException as e:
        return {"message": "Request failed", "status_code": 500, "error": str(e)}
    
    
if __name__ == "__main__":
    mcp.run(transport="stdio")

using Microsoft.AspNetCore.Mvc;

namespace {{ServiceName}}.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("/health")]
    public IActionResult Health() => Ok(new { status = "healthy", service = "{{ServiceName}}" });
}

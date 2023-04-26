class SiteNullContent(Exception):
    """
    the result of this pdp website is not showing anything
    probably a corrupted link or server not responding
    should try to request periodically and check
    """
    pass

# Error code
SITE_NULL_CONTENT = -1
SITE_MISSING_CRITICAL_CONTENT = -2
SITE_MISSING_CONTENT = -3

err_map = {
   -1 : "SITE_NULL_CONTENT",
   -2 : "SITE_MISSING_CRITICAL_CONTENT",
   -3 : "SITE_MISSING_CONTENT"
}

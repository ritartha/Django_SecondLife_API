// ============================================================
// SL Insight Dashboard — Scanner Object
// Place this script in a prim. It will periodically scan
// for avatars, collect region/parcel data, and POST to your
// Django API.
// ============================================================

// ── CONFIGURATION ──────────────────────────────────────────
string API_BASE    = "https://YOUR-DOMAIN.com";   // Your server URL (no trailing slash)
string API_KEY     = "your-lsl-api-key-change-me"; // Must match LSL_API_KEY in .env
float  SCAN_RANGE  = 96.0;                         // Scan radius in meters
float  SCAN_INTERVAL = 30.0;                       // Seconds between scans

// ── GLOBALS ────────────────────────────────────────────────
key    gRegionReq;
key    gAvatarReq;
key    gParcelReq;
list   gAvatarData;     // Accumulated JSON fragments
integer gAvatarCount;

// ── HELPERS ────────────────────────────────────────────────

string escapeJSON(string s)
{
    // Minimal JSON string escaping
    s = llReplaceSubString(s, "\\", "\\\\", 0);
    s = llReplaceSubString(s, "\"", "\\\"", 0);
    return s;
}

sendRegionData()
{
    string regionName = llGetRegionName();
    vector gridPos    = llGetRegionCorner() / 256.0;

    string mapURL = "https://map.secondlife.com/map-1-"
                  + (string)((integer)gridPos.x) + "-"
                  + (string)((integer)gridPos.y)
                  + "-objects.jpg";

    string body = "{\"name\":\"" + escapeJSON(regionName)
                + "\",\"map_image_url\":\"" + mapURL + "\"}";

    gRegionReq = llHTTPRequest(API_BASE + "/api/scan/region/",
        [HTTP_METHOD, "POST",
         HTTP_MIMETYPE, "application/json",
         HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
        body);
}

sendParcelData()
{
    string regionName = llGetRegionName();
    list   parcel     = llGetParcelDetails(llGetPos(),
                            [PARCEL_DETAILS_NAME,
                             PARCEL_DETAILS_DESC,
                             PARCEL_DETAILS_OWNER]);

    string parcelName = llList2String(parcel, 0);
    string parcelDesc = llList2String(parcel, 1);
    key    ownerKey   = llList2Key(parcel, 2);
    vector pos        = llGetPos();

    string coords = "(" + (string)((integer)pos.x) + ","
                       + (string)((integer)pos.y) + ","
                       + (string)((integer)pos.z) + ")";

    string body = "{\"region_name\":\"" + escapeJSON(regionName)
                + "\",\"name\":\""       + escapeJSON(parcelName)
                + "\",\"description\":\"" + escapeJSON(parcelDesc)
                + "\",\"owner_name\":\""  + escapeJSON((string)ownerKey)
                + "\",\"coordinates\":\"" + coords + "\"}";

    gParcelReq = llHTTPRequest(API_BASE + "/api/scan/parcels/",
        [HTTP_METHOD, "POST",
         HTTP_MIMETYPE, "application/json",
         HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
        body);
}

startAvatarScan()
{
    gAvatarData  = [];
    gAvatarCount = 0;
    llSensor("", "", AGENT, SCAN_RANGE, PI);
}

// ── STATES ─────────────────────────────────────────────────

default
{
    state_entry()
    {
        llOwnerSay("SL Insight Scanner initializing...");
        llSetTimerEvent(SCAN_INTERVAL);

        // Initial data push
        sendRegionData();
        sendParcelData();
        startAvatarScan();

        llOwnerSay("Scanner active. Range: " + (string)((integer)SCAN_RANGE)
                  + "m | Interval: " + (string)((integer)SCAN_INTERVAL) + "s");
    }

    timer()
    {
        sendRegionData();
        sendParcelData();
        startAvatarScan();
    }

    sensor(integer num)
    {
        string regionName = llGetRegionName();
        gAvatarData  = [];
        gAvatarCount = num;

        integer i;
        for (i = 0; i < num; ++i)
        {
            string avName = llDetectedName(i);
            key    avKey  = llDetectedKey(i);
            vector avPos  = llDetectedPos(i);
            float  dist   = llVecDist(llGetPos(), avPos);

            // Detect sitting
            integer isSitting = FALSE;
            // llGetAgentInfo returns bitmask
            integer info = llGetAgentInfo(avKey);
            if (info & AGENT_SITTING)
                isSitting = TRUE;

            // Count scripted attachments (limited info available)
            list attachments = llGetAttachedList(avKey);
            integer attCount  = llGetListLength(attachments);

            // Build attachment name list (UUIDs only in LSL)
            string attJSON = "[]";
            if (attCount > 0)
            {
                list attNames = [];
                integer a;
                for (a = 0; a < attCount && a < 10; ++a)
                {
                    attNames += ["\"att_" + (string)(a + 1) + "\""];
                }
                attJSON = "[" + llDumpList2String(attNames, ",") + "]";
            }

            string sitting = "false";
            if (isSitting) sitting = "true";

            string avJSON = "{\"name\":\"" + escapeJSON(avName)
                          + "\",\"uuid\":\"" + (string)avKey
                          + "\",\"distance\":" + (string)dist
                          + ",\"is_sitting\":" + sitting
                          + ",\"scripted_attachments_count\":" + (string)attCount
                          + ",\"attachments\":" + attJSON + "}";

            gAvatarData += [avJSON];
        }

        // Build and send payload
        string avatarsJSON = "[" + llDumpList2String(gAvatarData, ",") + "]";
        string body = "{\"region_name\":\"" + escapeJSON(regionName)
                    + "\",\"object_key\":\"" + (string)llGetKey()
                    + "\",\"avatars\":" + avatarsJSON + "}";

        gAvatarReq = llHTTPRequest(API_BASE + "/api/scan/avatars/",
            [HTTP_METHOD, "POST",
             HTTP_MIMETYPE, "application/json",
             HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
            body);
    }

    no_sensor()
    {
        // No avatars in range — send empty scan
        string regionName = llGetRegionName();
        string body = "{\"region_name\":\"" + escapeJSON(regionName)
                    + "\",\"object_key\":\"" + (string)llGetKey()
                    + "\",\"avatars\":[]}";

        gAvatarReq = llHTTPRequest(API_BASE + "/api/scan/avatars/",
            [HTTP_METHOD, "POST",
             HTTP_MIMETYPE, "application/json",
             HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
            body);
    }

    http_response(key req, integer code, list meta, string body)
    {
        if (req == gRegionReq)
        {
            if (code == 200)
                llOwnerSay("✓ Region data sent.");
            else
                llOwnerSay("✗ Region error " + (string)code + ": " + body);
        }
        else if (req == gAvatarReq)
        {
            if (code == 200)
                llOwnerSay("✓ Avatar scan sent (" + (string)gAvatarCount + " detected).");
            else
                llOwnerSay("✗ Avatar error " + (string)code + ": " + body);
        }
        else if (req == gParcelReq)
        {
            if (code == 200)
                llOwnerSay("✓ Parcel data sent.");
            else
                llOwnerSay("✗ Parcel error " + (string)code + ": " + body);
        }
    }

    on_rez(integer start)
    {
        llResetScript();
    }

    changed(integer change)
    {
        if (change & CHANGED_REGION)
        {
            llOwnerSay("Region changed. Re-initializing...");
            llResetScript();
        }
    }
}
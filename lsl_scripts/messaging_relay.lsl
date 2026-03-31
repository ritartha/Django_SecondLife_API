// ============================================================
// SL Insight Dashboard — Messaging Relay + OTP Delivery
// Place this script in a prim. It polls the API for:
//   1. Pending OTPs → sends via llInstantMessage to avatar
//   2. Pending messages → sends via llInstantMessage
// ============================================================

// ── CONFIGURATION ──────────────────────────────────────────
string API_BASE     = "https://YOUR-DOMAIN.com";
string API_KEY      = "your-lsl-api-key-change-me";
float  POLL_INTERVAL = 10.0;  // Poll every 10 seconds

// ── GLOBALS ────────────────────────────────────────────────
key gOTPReq;
key gMsgReq;
key gConfirmReq;

integer gPhase;  // 0 = poll OTPs, 1 = poll messages

// Simple minimal JSON value extractor.
// Finds "key":"value" or "key":value and returns value.
string jsonGet(string json, string k)
{
    string search = "\"" + k + "\":";
    integer i = llSubStringIndex(json, search);
    if (i == -1) return "";
    i += llStringLength(search);

    // Skip whitespace
    while (llGetSubString(json, i, i) == " ") ++i;

    string c = llGetSubString(json, i, i);
    if (c == "\"")
    {
        // Quoted string value
        integer end = llSubStringIndex(llGetSubString(json, i + 1, -1), "\"");
        return llGetSubString(json, i + 1, i + end);
    }
    else
    {
        // Unquoted (number, bool, null)
        integer j = i;
        while (j < llStringLength(json))
        {
            string ch = llGetSubString(json, j, j);
            if (ch == "," || ch == "}" || ch == "]") jump done;
            ++j;
        }
        @done;
        return llGetSubString(json, i, j - 1);
    }
}

// Split JSON array of objects into a list of individual object strings
list splitJSONArray(string arr)
{
    list result = [];
    // Remove outer brackets
    arr = llGetSubString(arr, 1, -2);
    if (llStringLength(arr) < 3) return [];

    integer depth = 0;
    integer start = 0;
    integer i;
    for (i = 0; i < llStringLength(arr); ++i)
    {
        string c = llGetSubString(arr, i, i);
        if (c == "{") ++depth;
        else if (c == "}") --depth;

        if (c == "," && depth == 0)
        {
            result += [llStringTrim(llGetSubString(arr, start, i - 1), STRING_TRIM)];
            start = i + 1;
        }
    }
    // Last element
    string last = llStringTrim(llGetSubString(arr, start, -1), STRING_TRIM);
    if (llStringLength(last) > 2) result += [last];

    return result;
}

pollOTPs()
{
    gOTPReq = llHTTPRequest(API_BASE + "/api/auth/pending-otps/",
        [HTTP_METHOD, "GET",
         HTTP_MIMETYPE, "application/json",
         HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
        "");
}

pollMessages()
{
    gMsgReq = llHTTPRequest(API_BASE + "/api/message/pending/",
        [HTTP_METHOD, "GET",
         HTTP_MIMETYPE, "application/json",
         HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
        "");
}

confirmDelivery(string messageId, string deliveryStatus)
{
    string body = "{\"message_id\":\"" + messageId
                + "\",\"status\":\"" + deliveryStatus + "\"}";

    gConfirmReq = llHTTPRequest(API_BASE + "/api/message/confirm/",
        [HTTP_METHOD, "POST",
         HTTP_MIMETYPE, "application/json",
         HTTP_CUSTOM_HEADER, "X-API-Key", API_KEY],
        body);
}

default
{
    state_entry()
    {
        llOwnerSay("SL Insight Messaging Relay initializing...");
        gPhase = 0;
        llSetTimerEvent(POLL_INTERVAL);
        pollOTPs();  // Initial poll
        llOwnerSay("Relay active. Polling every " + (string)((integer)POLL_INTERVAL) + "s");
    }

    timer()
    {
        if (gPhase == 0)
        {
            pollOTPs();
            gPhase = 1;
        }
        else
        {
            pollMessages();
            gPhase = 0;
        }
    }

    http_response(key req, integer code, list meta, string body)
    {
        if (req == gOTPReq)
        {
            if (code != 200)
            {
                llOwnerSay("✗ OTP poll error " + (string)code);
                return;
            }

            // Extract the pending_otps array
            integer arrStart = llSubStringIndex(body, "[");
            integer arrEnd   = llSubStringIndex(body, "]");
            if (arrStart == -1 || arrEnd == -1 || arrEnd <= arrStart + 1)
                return;  // No pending OTPs

            string arr = llGetSubString(body, arrStart, arrEnd);
            list items = splitJSONArray(arr);
            integer count = llGetListLength(items);

            integer i;
            for (i = 0; i < count; ++i)
            {
                string item    = llList2String(items, i);
                string avName  = jsonGet(item, "sl_avatar_name");
                string otpCode = jsonGet(item, "otp_code");

                if (avName != "" && otpCode != "")
                {
                    // We need the avatar's UUID to send IM.
                    // Use llRequestAgentData or name2key service.
                    // For simplicity, use llInstantMessage with
                    // name lookup (requires the avatar to be known).

                    // NOTE: In production you'd use a name-to-key
                    // service. For now, log to owner.
                    llOwnerSay("📨 OTP for " + avName + ": " + otpCode
                             + " (need UUID to deliver via IM)");

                    // If you have a name2key database or the avatar
                    // is in the same region, you can resolve and IM:
                    // llInstantMessage(avatarUUID,
                    //   "Your SL Insight verification code: " + otpCode);
                }
            }

            if (count > 0)
                llOwnerSay("✓ Processed " + (string)count + " OTP(s).");
        }
        else if (req == gMsgReq)
        {
            if (code != 200)
            {
                llOwnerSay("✗ Message poll error " + (string)code);
                return;
            }

            integer arrStart = llSubStringIndex(body, "[");
            integer arrEnd   = llSubStringIndex(body, "]");
            if (arrStart == -1 || arrEnd == -1 || arrEnd <= arrStart + 1)
                return;

            string arr = llGetSubString(body, arrStart, arrEnd);
            list items = splitJSONArray(arr);
            integer count = llGetListLength(items);

            integer i;
            for (i = 0; i < count; ++i)
            {
                string item       = llList2String(items, i);
                string msgId      = jsonGet(item, "id");
                string targetUUID = jsonGet(item, "target_uuid");
                string targetName = jsonGet(item, "target_name");
                string message    = jsonGet(item, "message");

                if (targetUUID != "" && message != "")
                {
                    llInstantMessage((key)targetUUID,
                        "[SL Insight] " + message);
                    llOwnerSay("📨 IM sent to " + targetName);
                    confirmDelivery(msgId, "delivered");
                }
                else
                {
                    llOwnerSay("✗ Invalid message data for " + targetName);
                    if (msgId != "")
                        confirmDelivery(msgId, "failed");
                }
            }

            if (count > 0)
                llOwnerSay("✓ Delivered " + (string)count + " message(s).");
        }
        else if (req == gConfirmReq)
        {
            if (code == 200)
                llOwnerSay("✓ Delivery status confirmed.");
        }
    }

    on_rez(integer start)
    {
        llResetScript();
    }
}
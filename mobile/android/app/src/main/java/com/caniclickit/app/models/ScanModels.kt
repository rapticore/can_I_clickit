package com.caniclickit.app.models

import com.google.gson.annotations.SerializedName

enum class ScanType {
    @SerializedName("text") TEXT,
    @SerializedName("url") URL,
    @SerializedName("screenshot") SCREENSHOT,
    @SerializedName("qr_code") QR_CODE
}

enum class ThreatLevel(val label: String) {
    @SerializedName("safe") SAFE("Safe"),
    @SerializedName("suspicious") SUSPICIOUS("Suspicious"),
    @SerializedName("dangerous") DANGEROUS("Dangerous")
}

enum class ConfidenceLevel(val label: String) {
    @SerializedName("high") HIGH("High confidence"),
    @SerializedName("medium") MEDIUM("Medium confidence"),
    @SerializedName("low") LOW("Low confidence")
}

data class ScanRequest(
    val content: String,
    @SerializedName("scan_type") val scanType: ScanType,
    val language: String = "en"
)

data class ScanResult(
    @SerializedName("scan_id") val id: String,
    @SerializedName("scan_type") val scanType: ScanType,
    @SerializedName("threat_level") val threatLevel: ThreatLevel,
    val confidence: ConfidenceLevel,
    @SerializedName("confidence_score") val confidenceScore: Double,
    @SerializedName("verdict_summary") val verdictSummary: String,
    @SerializedName("consequence_warning") val consequenceWarning: String?,
    @SerializedName("safe_action_suggestion") val safeAction: String?,
    val explanation: String,
    val signals: List<SignalResult> = emptyList(),
    @SerializedName("scam_pattern") val threatCategory: String?,
    @SerializedName("created_at") val scannedAt: String,
    val disclaimer: String = ""
) {
    val plainLanguageSummary: String
        get() = explanation
}

data class SignalResult(
    val source: String,
    val score: Double,
    val detail: String
)

data class ScreenshotScanRequest(
    @SerializedName("image_base64") val imageBase64: String,
    val language: String = "en"
)

data class FeedbackRequest(
    @SerializedName("scan_id") val scanId: String,
    @SerializedName("user_verdict") val userVerdict: String,
    val comment: String? = null
) {
    constructor(scanId: String, isHelpful: Boolean) : this(
        scanId = scanId,
        userVerdict = if (isHelpful) "correct" else "incorrect_false_negative",
    )
}

data class HealthResponse(
    val status: String,
    val checks: Map<String, String>? = null
)

package com.caniclickit.app.models

import com.google.gson.annotations.SerializedName

enum class ThreatCategory(val label: String, val description: String) {
    @SerializedName("credential_theft")
    CREDENTIAL_THEFT("Password Stolen", "Someone may have your password"),

    @SerializedName("financial_fraud")
    FINANCIAL_FRAUD("Money Scam", "Someone may have your payment details"),

    @SerializedName("identity_theft")
    IDENTITY_THEFT("Identity Theft", "Someone may use your personal information"),

    @SerializedName("malware_download")
    MALWARE_DOWNLOAD("Malware Risk", "A harmful file may have been installed"),

    @SerializedName("gift_card_wire")
    GIFT_CARD_WIRE("Gift Card/Wire Scam", "Money transfer scam indicators"),

    @SerializedName("remote_access")
    REMOTE_ACCESS("Remote Access Scam", "Someone may have remote control of your device"),

    @SerializedName("general_unknown")
    GENERAL_UNKNOWN("General Safety", "Follow general protection steps"),

    @SerializedName("blackmail_sextortion")
    BLACKMAIL_SEXTORTION("Blackmail/Sextortion", "Threat message demanding payment"),

    @SerializedName("ransomware_extortion")
    RANSOMWARE_EXTORTION("Ransomware Extortion", "Message claims files are encrypted"),

    @SerializedName("pig_butchering")
    PIG_BUTCHERING("Pig Butchering", "Romance/investment scam pattern")
}

enum class UrgencyLevel {
    @SerializedName("critical") CRITICAL,
    @SerializedName("high") HIGH,
    @SerializedName("medium") MEDIUM
}

enum class StepUrgency(val displayName: String) {
    IMMEDIATE("Do this now"),
    SOON("Do this today"),
    LATER("Do this when you can")
}

data class RecoveryChecklist(
    val category: ThreatCategory,
    val urgency: UrgencyLevel,
    val title: String,
    @SerializedName("opening_message") val openingMessage: String,
    val steps: List<RecoveryStep>,
    @SerializedName("quick_dial_contacts") val emergencyContacts: List<QuickDialContact> = emptyList(),
    val disclaimer: String = ""
) {
    val description: String
        get() = openingMessage
}

data class RecoveryStep(
    @SerializedName("step_number") val stepNumber: Int,
    val title: String,
    val description: String,
    @SerializedName("help_detail") val helpDetail: String = "",
    @SerializedName("action_type") val actionType: String = "info",
    @SerializedName("action_data") val actionData: Map<String, Any>? = null
) {
    val id: String
        get() = "step-$stepNumber"

    val plainLanguage: String
        get() = if (helpDetail.isNotBlank()) helpDetail else description

    val isCritical: Boolean
        get() = actionType == "urgent" || actionType == "critical"

    val externalLink: String?
        get() = actionData?.get("url")?.toString()

    val externalLinkLabel: String?
        get() = actionData?.get("label")?.toString()

    val urgency: StepUrgency
        get() = when {
            isCritical -> StepUrgency.IMMEDIATE
            actionType == "warning" -> StepUrgency.SOON
            else -> StepUrgency.LATER
        }
}

data class TriageQuestion(
    val id: String,
    val question: String,
    val options: List<TriageOption>,
    @SerializedName("allow_multiple") val allowMultiple: Boolean = false
)

data class TriageOption(
    val id: String,
    val label: String,
    @SerializedName("maps_to") val mapsToCategory: String? = null,
    @SerializedName("plain_language") val plainLanguage: String? = null
)

data class TriageRequest(
    val answers: List<TriageAnswerSubmission>
)

data class TriageAnswerSubmission(
    @SerializedName("question_id") val questionId: String,
    @SerializedName("selected_option_id") val selectedOptionId: String
)

data class TriageResult(
    val category: ThreatCategory,
    val confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM,
    val message: String = ""
)

data class QuickDialContact(
    val name: String,
    val phone: String,
    val description: String = ""
)

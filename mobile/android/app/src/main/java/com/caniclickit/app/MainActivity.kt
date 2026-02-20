package com.caniclickit.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import androidx.navigation.compose.rememberNavController
import com.caniclickit.app.models.*
import com.caniclickit.app.navigation.AppNavGraph
import com.caniclickit.app.navigation.Routes
import com.caniclickit.app.network.ApiClient
import com.caniclickit.app.services.SpeechService
import com.caniclickit.app.ui.theme.CanIClickItTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private lateinit var speechService: SpeechService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        speechService = SpeechService(this)
        speechService.initialize()

        val sharedText = extractSharedText(intent)

        setContent {
            CanIClickItTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppRoot(
                        speechService = speechService,
                        initialSharedText = sharedText
                    )
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        speechService.shutdown()
    }

    private fun extractSharedText(intent: Intent?): String? {
        if (intent?.action != Intent.ACTION_SEND) return null
        return when {
            intent.type?.startsWith("text/") == true ->
                intent.getStringExtra(Intent.EXTRA_TEXT)
            else -> null
        }
    }
}

@Composable
private fun AppRoot(
    speechService: SpeechService,
    initialSharedText: String?
) {
    val navController = rememberNavController()

    var isGrandmaMode by remember { mutableStateOf(false) }
    var selectedLanguage by remember { mutableStateOf("en") }

    var scanResult by remember { mutableStateOf<ScanResult?>(null) }
    var scanHistory by remember { mutableStateOf<List<ScanResult>>(emptyList()) }
    var isScanning by remember { mutableStateOf(false) }

    var triageQuestions by remember { mutableStateOf<List<TriageQuestion>>(emptyList()) }
    var triageResult by remember { mutableStateOf<TriageResult?>(null) }
    var checklist by remember { mutableStateOf<RecoveryChecklist?>(null) }
    var isLoadingTriage by remember { mutableStateOf(false) }
    var isLoadingChecklist by remember { mutableStateOf(false) }

    val isListening by speechService.isListening.collectAsState()
    val recognizedText by speechService.recognizedText.collectAsState()

    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        try {
            val response = ApiClient.api.getTriageQuestions()
            if (response.isSuccessful) {
                triageQuestions = response.body()?.questions ?: emptyList()
            }
        } catch (_: Exception) {
            triageQuestions = emptyList()
        }
    }

    AppNavGraph(
        navController = navController,
        isGrandmaMode = isGrandmaMode,
        selectedLanguage = selectedLanguage,
        scanResult = scanResult,
        scanHistory = scanHistory,
        triageQuestions = triageQuestions,
        checklist = checklist,
        triageResult = triageResult,
        isScanning = isScanning,
        isListening = isListening,
        isLoadingTriage = isLoadingTriage,
        isLoadingChecklist = isLoadingChecklist,
        recognizedText = recognizedText,
        sharedText = initialSharedText,
        onScan = { text ->
            coroutineScope.launch {
                    isScanning = true
                    try {
                        val type = detectScanType(text)
                        val response = ApiClient.api.scan(ScanRequest(text, type))
                        if (response.isSuccessful) {
                            response.body()?.let { result ->
                                scanResult = result
                            scanHistory = listOf(result) + scanHistory
                        }
                    }
                } catch (_: Exception) {
                    // Network error handling would go here
                } finally {
                    isScanning = false
                }
            }
        },
        onScanScreenshot = { base64 ->
            coroutineScope.launch {
                isScanning = true
                try {
                    val response = ApiClient.api.scanScreenshot(ScreenshotScanRequest(base64))
                    if (response.isSuccessful) {
                        response.body()?.let { result ->
                            scanResult = result
                            scanHistory = listOf(result) + scanHistory
                        }
                    }
                } catch (_: Exception) {
                } finally {
                    isScanning = false
                }
            }
        },
        onVoiceInput = {
            speechService.startListening()
        },
        onStopVoice = {
            speechService.stopListening()
        },
        onFeedback = { scanId, isHelpful ->
            coroutineScope.launch {
                try {
                    ApiClient.api.submitFeedback(FeedbackRequest(scanId, isHelpful))
                } catch (_: Exception) {
                }
            }
        },
        onSubmitTriage = { answers ->
            coroutineScope.launch {
                isLoadingTriage = true
                try {
                    val response = ApiClient.api.triage(TriageRequest(answers))
                    if (response.isSuccessful) {
                        response.body()?.let { recoveredChecklist ->
                            checklist = recoveredChecklist
                            triageResult = TriageResult(
                                category = recoveredChecklist.category,
                                message = recoveredChecklist.openingMessage
                            )
                        }
                    }
                } catch (_: Exception) {
                } finally {
                    isLoadingTriage = false
                    isLoadingChecklist = false
                }
            }
        },
        onStepCompleted = { stepId ->
            // Track completed step locally
        },
        onCallForHelp = {
            // Open dialer with FTC number as default
            val intent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:18773824357")
            }
            navController.context.startActivity(intent)
        },
        onFamilyAlert = {
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(
                    Intent.EXTRA_TEXT,
                    "I may have been targeted by a scam. Can you help me? " +
                        "I'm using the 'Can I Click It?' app to figure out next steps."
                )
            }
            navController.context.startActivity(
                Intent.createChooser(intent, "Alert someone you trust")
            )
        },
        onGrandmaModeToggle = { enabled ->
            isGrandmaMode = enabled
            if (enabled) {
                navController.navigate(Routes.GRANDMA_MODE) {
                    popUpTo(Routes.HOME) { inclusive = true }
                }
            } else {
                navController.navigate(Routes.HOME) {
                    popUpTo(Routes.GRANDMA_MODE) { inclusive = true }
                }
            }
        },
        onLanguageSelected = { language ->
            selectedLanguage = language
        }
    )
}

private fun detectScanType(text: String): ScanType {
    val trimmed = text.trim()
    return when {
        trimmed.matches(Regex("^https?://.*")) -> ScanType.URL
        trimmed.matches(Regex("^www\\..*")) -> ScanType.URL
        else -> ScanType.TEXT
    }
}

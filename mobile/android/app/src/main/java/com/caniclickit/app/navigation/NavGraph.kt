package com.caniclickit.app.navigation

import androidx.compose.runtime.*
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.caniclickit.app.models.*
import com.caniclickit.app.ui.screens.*

object Routes {
    const val HOME = "home"
    const val SCAN = "scan"
    const val SCAN_WITH_TEXT = "scan/{text}"
    const val VERDICT = "verdict"
    const val RECOVERY = "recovery"
    const val SCAN_HISTORY = "scan_history"
    const val GRANDMA_MODE = "grandma_mode"
    const val QR_SCANNER = "qr_scanner"
    const val SETTINGS = "settings"
}

@Composable
fun AppNavGraph(
    navController: NavHostController,
    isGrandmaMode: Boolean,
    selectedLanguage: String,
    scanResult: ScanResult?,
    scanHistory: List<ScanResult>,
    triageQuestions: List<TriageQuestion>,
    checklist: RecoveryChecklist?,
    triageResult: TriageResult?,
    isScanning: Boolean,
    isListening: Boolean,
    isLoadingTriage: Boolean,
    isLoadingChecklist: Boolean,
    recognizedText: String,
    sharedText: String?,
    onScan: (String) -> Unit,
    onScanScreenshot: (String) -> Unit,
    onVoiceInput: () -> Unit,
    onStopVoice: () -> Unit,
    onFeedback: (String, Boolean) -> Unit,
    onSubmitTriage: (List<TriageAnswerSubmission>) -> Unit,
    onStepCompleted: (String) -> Unit,
    onCallForHelp: () -> Unit,
    onFamilyAlert: () -> Unit,
    onGrandmaModeToggle: (Boolean) -> Unit,
    onLanguageSelected: (String) -> Unit
) {
    val startDestination = if (isGrandmaMode) Routes.GRANDMA_MODE else Routes.HOME

    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Routes.HOME) {
            HomeScreen(
                isGrandmaMode = isGrandmaMode,
                onCheckSomething = {
                    if (sharedText != null) {
                        navController.navigate("scan/$sharedText")
                    } else {
                        navController.navigate(Routes.SCAN)
                    }
                },
                onScanQr = { navController.navigate(Routes.QR_SCANNER) },
                onAlreadyClicked = { navController.navigate(Routes.RECOVERY) },
                onSettings = { navController.navigate(Routes.SETTINGS) },
                onHistory = { navController.navigate(Routes.SCAN_HISTORY) }
            )
        }

        composable(Routes.SCAN) {
            ScanScreen(
                initialText = sharedText.orEmpty(),
                isLoading = isScanning,
                isListening = isListening,
                onScan = { text ->
                    onScan(text)
                    navController.navigate(Routes.VERDICT)
                },
                onVoiceInput = onVoiceInput,
                onStopVoice = onStopVoice,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SCAN_WITH_TEXT) { backStackEntry ->
            val text = backStackEntry.arguments?.getString("text").orEmpty()
            ScanScreen(
                initialText = text,
                isLoading = isScanning,
                isListening = isListening,
                onScan = { scanText ->
                    onScan(scanText)
                    navController.navigate(Routes.VERDICT)
                },
                onVoiceInput = onVoiceInput,
                onStopVoice = onStopVoice,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.VERDICT) {
            scanResult?.let { result ->
                VerdictScreen(
                    scanResult = result,
                    onFeedback = { isHelpful -> onFeedback(result.id, isHelpful) },
                    onBack = { navController.popBackStack() }
                )
            }
        }

        composable(Routes.RECOVERY) {
            RecoveryScreen(
                triageQuestions = triageQuestions,
                checklist = checklist,
                triageResult = triageResult,
                isLoadingTriage = isLoadingTriage,
                isLoadingChecklist = isLoadingChecklist,
                onSubmitTriage = onSubmitTriage,
                onStepCompleted = onStepCompleted,
                onCallForHelp = onCallForHelp,
                onFamilyAlert = onFamilyAlert,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SCAN_HISTORY) {
            ScanHistoryScreen(
                scans = scanHistory,
                onScanClick = { scan ->
                    navController.navigate(Routes.VERDICT)
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.GRANDMA_MODE) {
            GrandmaModeScreen(
                isLoading = isScanning,
                isListening = isListening,
                recognizedText = recognizedText,
                onScan = { text ->
                    onScan(text)
                    navController.navigate(Routes.VERDICT)
                },
                onVoiceInput = onVoiceInput,
                onStopVoice = onStopVoice,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.QR_SCANNER) {
            QRScannerScreen(
                onQRCodeScanned = { url ->
                    navController.popBackStack()
                    navController.navigate("scan/$url")
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SETTINGS) {
            SettingsScreen(
                isGrandmaMode = isGrandmaMode,
                selectedLanguage = selectedLanguage,
                availableLanguages = listOf(
                    "en" to "English",
                    "es" to "Español",
                    "fr" to "Français",
                    "zh" to "中文",
                    "hi" to "हिन्दी",
                    "ar" to "العربية"
                ),
                onGrandmaModeToggle = onGrandmaModeToggle,
                onLanguageSelected = onLanguageSelected,
                onBack = { navController.popBackStack() }
            )
        }
    }
}

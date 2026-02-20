package com.caniclickit.app.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.caniclickit.app.models.*
import com.caniclickit.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecoveryScreen(
    triageQuestions: List<TriageQuestion>,
    checklist: RecoveryChecklist?,
    triageResult: TriageResult?,
    isLoadingTriage: Boolean,
    isLoadingChecklist: Boolean,
    onSubmitTriage: (List<TriageAnswerSubmission>) -> Unit,
    onStepCompleted: (String) -> Unit,
    onCallForHelp: () -> Unit,
    onFamilyAlert: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    var currentPhase by remember { mutableStateOf(if (triageQuestions.isNotEmpty()) Phase.TRIAGE else Phase.LOADING) }
    var completedSteps by remember { mutableStateOf(setOf<String>()) }
    var currentStepIndex by remember { mutableIntStateOf(0) }
    val triageAnswers = remember { mutableStateMapOf<String, List<String>>() }

    LaunchedEffect(triageResult) {
        if (triageResult != null) currentPhase = Phase.CHECKLIST
    }

    LaunchedEffect(checklist) {
        if (checklist != null) currentPhase = Phase.CHECKLIST
    }

    LaunchedEffect(triageQuestions) {
        if (checklist == null) {
            currentPhase = if (triageQuestions.isNotEmpty()) Phase.TRIAGE else Phase.LOADING
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Let's Fix This") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                }
            )
        },
        bottomBar = {
            Surface(
                tonalElevation = 3.dp,
                shadowElevation = 8.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Button(
                        onClick = onCallForHelp,
                        modifier = Modifier
                            .weight(1f)
                            .height(56.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = SeverityCritical
                        ),
                        shape = MaterialTheme.shapes.medium
                    ) {
                        Icon(Icons.Default.Phone, null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Call for Help", style = MaterialTheme.typography.labelLarge)
                    }
                    OutlinedButton(
                        onClick = onFamilyAlert,
                        modifier = Modifier.height(56.dp),
                        shape = MaterialTheme.shapes.medium
                    ) {
                        Icon(Icons.Default.People, null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Alert Family")
                    }
                }
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Reassuring opening
            Card(
                colors = CardDefaults.cardColors(containerColor = SeverityInfoBg),
                shape = MaterialTheme.shapes.medium
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(Icons.Default.Favorite, null, tint = SeverityInfo)
                    Text(
                        "Don't worry — let's fix this together.",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.SemiBold,
                        color = SeverityInfo
                    )
                }
            }

            when (currentPhase) {
                Phase.LOADING -> {
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }

                Phase.TRIAGE -> {
                    Text(
                        "First, tell us what happened:",
                        style = MaterialTheme.typography.titleMedium
                    )

                    triageQuestions.forEach { question ->
                        TriageQuestionCard(
                            question = question,
                            selectedAnswers = triageAnswers[question.id] ?: emptyList(),
                            onAnswerSelected = { answerId ->
                                val current = triageAnswers[question.id]?.toMutableList() ?: mutableListOf()
                                if (question.allowMultiple) {
                                    if (answerId in current) current.remove(answerId) else current.add(answerId)
                                } else {
                                    current.clear()
                                    current.add(answerId)
                                }
                                triageAnswers[question.id] = current
                            }
                        )
                    }

                    Button(
                        onClick = {
                            val submissions = triageAnswers.map { (qId, aIds) ->
                                TriageAnswerSubmission(qId, aIds.firstOrNull().orEmpty())
                            }.filter { it.selectedOptionId.isNotBlank() }
                            onSubmitTriage(submissions)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        enabled = triageAnswers.isNotEmpty() && !isLoadingTriage,
                        shape = MaterialTheme.shapes.medium
                    ) {
                        if (isLoadingTriage) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                strokeWidth = 2.dp,
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                        } else {
                            Text("Get My Recovery Plan")
                        }
                    }
                }

                Phase.CHECKLIST -> {
                    if (isLoadingChecklist) {
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator()
                        }
                    } else if (checklist != null) {
                        Text(
                            checklist.title,
                            style = MaterialTheme.typography.titleLarge
                        )
                        Text(
                            checklist.description,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        // Progress bar
                        val progress = if (checklist.steps.isNotEmpty()) {
                            completedSteps.size.toFloat() / checklist.steps.size
                        } else 0f

                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    "Progress",
                                    style = MaterialTheme.typography.labelMedium
                                )
                                Text(
                                    "${completedSteps.size} of ${checklist.steps.size}",
                                    style = MaterialTheme.typography.labelMedium
                                )
                            }
                            LinearProgressIndicator(
                                progress = { progress },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(8.dp),
                                color = SeveritySafe,
                                trackColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        }

                        // Show one step at a time
                        val currentStep = checklist.steps.getOrNull(currentStepIndex)
                        if (currentStep != null) {
                            RecoveryStepCard(
                                step = currentStep,
                                stepNumber = currentStepIndex + 1,
                                totalSteps = checklist.steps.size,
                                isCompleted = currentStep.id in completedSteps,
                                onDone = {
                                    completedSteps = completedSteps + currentStep.id
                                    onStepCompleted(currentStep.id)
                                    if (currentStepIndex < checklist.steps.size - 1) {
                                        currentStepIndex++
                                    }
                                },
                                onOpenLink = { url ->
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                                    context.startActivity(intent)
                                }
                            )
                        } else {
                            // All done
                            Card(
                                colors = CardDefaults.cardColors(containerColor = SeveritySafeBg),
                                shape = MaterialTheme.shapes.medium
                            ) {
                                Column(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(24.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Icon(
                                        Icons.Default.CheckCircle,
                                        null,
                                        tint = SeveritySafe,
                                        modifier = Modifier.size(48.dp)
                                    )
                                    Spacer(Modifier.height(12.dp))
                                    Text(
                                        "You've completed all the steps!",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = SeveritySafe
                                    )
                                    Text(
                                        "You're in a much safer place now.",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Disclaimer
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "This guidance is our best recommendation. When in doubt, contact your bank or local authorities.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
private fun TriageQuestionCard(
    question: TriageQuestion,
    selectedAnswers: List<String>,
    onAnswerSelected: (String) -> Unit
) {
    Card(
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                question.question,
                style = MaterialTheme.typography.titleMedium
            )
            question.options.forEach { option ->
                val isSelected = option.id in selectedAnswers
                FilterChip(
                    selected = isSelected,
                    onClick = { onAnswerSelected(option.id) },
                    label = {
                        Text(
                            option.plainLanguage ?: option.label,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = 48.dp),
                    shape = MaterialTheme.shapes.small
                )
            }
        }
    }
}

@Composable
private fun RecoveryStepCard(
    step: RecoveryStep,
    stepNumber: Int,
    totalSteps: Int,
    isCompleted: Boolean,
    onDone: () -> Unit,
    onOpenLink: (String) -> Unit
) {
    Card(
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(
            containerColor = if (step.isCritical)
                SeverityHighBg
            else
                MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (step.isCritical) {
                    Icon(
                        Icons.Default.PriorityHigh,
                        null,
                        tint = SeverityHigh,
                        modifier = Modifier.size(20.dp)
                    )
                }
                Text(
                    "Step $stepNumber of $totalSteps",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Text(
                step.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )

            Text(
                step.plainLanguage,
                style = MaterialTheme.typography.bodyLarge
            )

            step.externalLink?.let { link ->
                TextButton(onClick = { onOpenLink(link) }) {
                    Icon(Icons.Default.OpenInNew, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(4.dp))
                    Text(step.externalLinkLabel ?: "Open link")
                }
            }

            Button(
                onClick = onDone,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                enabled = !isCompleted,
                shape = MaterialTheme.shapes.medium,
                colors = ButtonDefaults.buttonColors(
                    containerColor = SeveritySafe
                )
            ) {
                Icon(Icons.Default.Check, null, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(if (isCompleted) "Done" else "Mark as Done")
            }
        }
    }
}

private enum class Phase {
    LOADING, TRIAGE, CHECKLIST
}

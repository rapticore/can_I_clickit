package com.caniclickit.app.network

import com.caniclickit.app.BuildConfig
import com.caniclickit.app.models.*
import com.google.gson.annotations.SerializedName
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.util.concurrent.TimeUnit

interface CanIClickItApi {

    @POST("v1/scan")
    suspend fun scan(@Body request: ScanRequest): Response<ScanResult>

    @POST("v1/scan/screenshot/base64")
    suspend fun scanScreenshot(@Body request: ScreenshotScanRequest): Response<ScanResult>

    @GET("v1/recovery/triage/questions")
    suspend fun getTriageQuestions(): Response<TriageQuestionsResponse>

    @POST("v1/recovery/triage")
    suspend fun triage(@Body request: TriageRequest): Response<RecoveryChecklist>

    @GET("v1/recovery/checklist/{category}")
    suspend fun getChecklist(@Path("category") category: String): Response<RecoveryChecklist>

    @POST("v1/feedback")
    suspend fun submitFeedback(@Body request: FeedbackRequest): Response<FeedbackResponse>

    @GET("v1/health")
    suspend fun health(): Response<HealthResponse>
}

data class TriageQuestionsResponse(
    val questions: List<TriageQuestion>
)

data class FeedbackResponse(
    @SerializedName("feedback_id") val feedbackId: String,
    @SerializedName("scan_id") val scanId: String,
    val acknowledged: Boolean
)

object ApiClient {

    private var apiKey: String = BuildConfig.API_KEY

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }

    private val httpClient = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("X-API-Key", apiKey)
                .addHeader("Accept", "application/json")
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL.trimEnd('/') + "/")
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: CanIClickItApi = retrofit.create(CanIClickItApi::class.java)

    fun setApiKey(key: String) {
        apiKey = key
    }
}

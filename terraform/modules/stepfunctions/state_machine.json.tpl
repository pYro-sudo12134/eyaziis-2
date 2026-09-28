{
  "Comment": "Speech synthesis and Q&A pipeline",
  "StartAt": "CheckInputType",
  "States": {
    "CheckInputType": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.input_type",
          "StringEquals": "audio",
          "Next": "StartTranscription"
        }
      ],
      "Default": "Formalize"
    },

    "StartTranscription": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_transcribe_arn}",
        "Payload": {
          "action": "start",
          "request_id.$": "$.request_id",
          "s3_uri.$": "$.s3_uri"
        }
      },
      "ResultPath": "$.transcription",
      "Next": "WaitForTranscription"
    },

    "WaitForTranscription": {
      "Type": "Wait",
      "Seconds": 5,
      "Next": "CheckTranscription"
    },

    "CheckTranscription": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_transcribe_arn}",
        "Payload": {
          "action": "check",
          "job_name.$": "$.transcription.job_name",
          "attempts.$": "$.transcription.attempts"
        }
      },
      "ResultPath": "$.transcription",
      "Next": "IsTranscriptionDone"
    },

    "IsTranscriptionDone": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.transcription.status",
          "StringEquals": "COMPLETED",
          "Next": "ParseTranscript"
        },
        {
          "Variable": "$.transcription.status",
          "StringEquals": "FAILED",
          "Next": "TranscriptionFailed"
        },
        {
          "Variable": "$.transcription.attempts",
          "NumericGreaterThanEquals": 60,
          "Next": "TranscriptionTimeout"
        }
      ],
      "Default": "WaitForTranscription"
    },

    "ParseTranscript": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_transcribe_arn}",
        "Payload": {
          "action": "parse",
          "job_name.$": "$.transcription.job_name"
        }
      },
      "ResultPath": "$.transcription",
      "Next": "MergeTranscript"
    },

    "MergeTranscript": {
      "Type": "Pass",
      "Parameters": {
        "request_id.$": "$.request_id",
        "input_type.$": "$.input_type",
        "text.$": "$.transcription.text",
        "voice.$": "$.voice",
        "speed.$": "$.speed",
        "volume.$": "$.volume",
        "pitch.$": "$.pitch",
        "format.$": "$.format"
      },
      "Next": "Formalize"
    },

    "TranscriptionFailed": {
      "Type": "Fail",
      "Error": "TranscriptionFailed"
    },

    "TranscriptionTimeout": {
      "Type": "Fail",
      "Error": "TranscriptionTimeout"
    },

    "Formalize": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_formalize_arn}",
        "Payload.$": "$"
      },
      "ResultPath": null,
      "Next": "Execute"
    },

    "Execute": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_execute_arn}",
        "Payload.$": "$"
      },
      "ResultPath": null,
      "Next": "SendToTTS"
    },

    "SendToTTS": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "${sqs_tts_url}",
        "MessageBody.$": "$"
      },
      "ResultPath": null,
      "End": true
    }
  }
}
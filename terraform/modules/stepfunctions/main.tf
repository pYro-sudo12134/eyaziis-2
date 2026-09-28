resource "aws_sfn_state_machine" "this" {
  name     = "pipeline-${var.environment}"
  role_arn = var.sfn_role_arn

  definition = templatefile("${path.module}/state_machine.json.tpl", {
    lambda_formalize_arn = var.lambda_function_arns["formalize"]
    lambda_execute_arn   = var.lambda_function_arns["execute"]
    lambda_transcribe_arn = var.lambda_function_arns["transcribe"]
    sqs_tts_url          = var.sqs_tts_url
  })
}
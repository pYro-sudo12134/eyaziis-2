resource "aws_sqs_queue" "dlq" {
  for_each = var.queues
  name     = "${each.key}-dlq-${var.environment}"
}

resource "aws_sqs_queue" "this" {
  for_each                   = var.queues
  name                       = "${each.key}-${var.environment}"
  visibility_timeout_seconds = each.value.visibility_timeout

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq[each.key].arn
    maxReceiveCount     = each.value.max_receive_count
  })
}
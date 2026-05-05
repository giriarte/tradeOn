* Create StrategyMonitorQueue.
  * This is the trigger queue for messages that will be sent to StrategyMonitorLambda

* Create ActiveSubscriptionGatherer lambda
  * this lambda will collect all the users with active subscriptions
  * Right after that, it will send a message to StrategyMonitorQueue

* Test the whole flow by creating 2 users with active subscriptions, creating strategies in the UI, and verify that both lambdas are able to process the records for them
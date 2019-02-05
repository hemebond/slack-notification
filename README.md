# Slack Notification

![Example Notification Messages](example-notifications.png?raw=true)

## Icinga2

Here is an example of Icinga2 configuration objects:

    template NotificationCommand "slack-notification-command"  {
            import "plugin-notification-command"

            command = [ SysconfDir + "/icinga2/scripts/slack-notification.py", ]
            arguments += {
                    "-a" = "$notification.author$"
                    "-c" = "$notification.comment$"
                    "-C" = "$slack_channel$"
                    "-u" = "$slack_webhook_url$"
                    "-t" = "$notification.type$"
                    "-w" = "https://icinga.domain.com"
            }
            vars.slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    }
    object NotificationCommand "slack-notification-command-host"  {
            import "slack-notification-command"

            arguments += {
                    "-m" = "$host.output$"
                    "-H" = "$host.name$"
                    "-s" = "$host.state$"
            }
    }
    object NotificationCommand "slack-notification-command-service"  {
            import "slack-notification-command"

            arguments += {
                    "-m" = "$service.output$"
                    "-s" = "$service.state$"
                    "-H" = "$host.display_name$"
                    "-S" = "$service.name$"
            }
    }

    object User "slack"  {
        // Override the default notification webhook
        vars.slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    }

    object Notification "website-notifications" {
            command = "slack-notification-command-host"
            host_name = "localhost"
            users = [ "slack", ]
    }

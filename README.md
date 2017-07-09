# Slack Notification

![Example Notification Messages](example-notifications.png?raw=true)

## Icinga2

Here is an example of Icinga2 NotificationCommand objects:

    object NotificationCommand "slack-host-notification"  {
            import "plugin-notification-command"
            command = [ SysconfDir + "/icinga2/scripts/slack-notification.py", ]

            arguments = {
                    "-u" = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
                    "-w" = "https://icingaweb2.mycompany.com"
                    
                    "-t" = "$notification.type$"
                    "-a" = "$notification.author$"
                    "-c" = "$notification.comment$"
                    
                    "-H" = "$host.name$"
                    "-s" = "$host.state$"
                    "-m" = "$host.output$"
            }
    }
    object NotificationCommand "slack-service-notification"  {
            import "plugin-notification-command"

            command = [ SysconfDir + "/icinga2/scripts/slack-notification.py", ]
            arguments = {
                    "-u" = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
                    "-w" = "https://icingaweb2.mycompany.com"
                    
                    "-t" = "$notification.type$"
                    "-a" = "$notification.author$"
                    "-c" = "$notification.comment$"
                    
                    "-S" = "$service.name$"
                    "-s" = "$service.state$"
                    "-m" = "$service.output$"
                    "-H" = "$host.display_name$"
            }
    }

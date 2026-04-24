from dataclasses import dataclass


@dataclass(frozen=True)
class Mail:
    sender: str
    recipient: str
    title: str
    message: str


mail_data: list[Mail] = [
    Mail(
        sender="alice@example.com",
        recipient="bob@example.com",
        title="Project Update",
        message="Hi Bob, just wanted to update you on the project progress. We're on track for the deadline.",
    ),
    Mail(
        sender="john.smith@company.com",
        recipient="sarah.jones@company.com",
        title="Meeting Reminder",
        message="Don't forget about our team meeting tomorrow at 2 PM in Conference Room B.",
    ),
    Mail(
        sender="support@service.com",
        recipient="user123@email.com",
        title="Your Order Has Shipped",
        message="Great news! Your order #12345 has been shipped and should arrive within 3-5 business days.",
    ),
    Mail(
        sender="newsletter@techblog.com",
        recipient="subscriber@gmail.com",
        title="Weekly Tech Digest",
        message="Check out this week's top articles on AI, cloud computing, and software development best practices.",
    ),
    Mail(
        sender="hr@corporation.com",
        recipient="employee@corporation.com",
        title="Benefits Enrollment Deadline",
        message="Reminder: The deadline to enroll in next year's benefits is December 15th. Please complete your selection soon.",
    ),
    Mail(
        sender="team-lead@startup.io",
        recipient="developer@startup.io",
        title="Code Review Request",
        message="Hey, could you review PR #234 when you get a chance? It includes the new authentication feature.",
    ),
    Mail(
        sender="marketing@brand.com",
        recipient="customers@lists.com",
        title="Exclusive 20% Off Sale",
        message="For a limited time, enjoy 20% off all products! Use code SAVE20 at checkout. Offer ends Sunday.",
    ),
    Mail(
        sender="security@bank.com",
        recipient="account.holder@email.com",
        title="Security Alert: Password Changed",
        message="Your account password was recently changed. If this wasn't you, please contact us immediately.",
    ),
    Mail(
        sender="events@conference.org",
        recipient="attendee@company.com",
        title="Conference Schedule Available",
        message="The full schedule for DevCon 2026 is now live! Browse sessions and plan your conference experience.",
    ),
    Mail(
        sender="noreply@automation.com",
        recipient="admin@website.com",
        title="Daily Backup Completed",
        message="Automated backup completed successfully at 2:00 AM. All systems operational.",
    ),
]

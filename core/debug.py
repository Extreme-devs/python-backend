from rich.console import Console

console = Console(log_path=False)

def here():
    console.print("-" * 5 + "HERE" + "-" * 5, style="bold red")

def press_enter_to_continue():
    console.print("\nPress Enter to continue...\n", style="bold red")
    input()


def error_message(message, newline=False):
    if newline:
        console.log(f"\n[red][bold]Error:[/bold] {message}[/red]")
    else:
        console.log(f"[red][bold]Error:[/bold] {message}[/red]")


def success_message(message, newline=False):
    if newline:
        console.log(f"\n[green][bold]Success:[/bold] {message}[/green]")
    else:
        console.log(f"[green][bold]Success:[/bold] {message}[/green]")


def info_message(message):
    console.log(f"[yellow]{message}[/yellow]")


def warning_message(message):
    console.log(f"[cyan][bold]Warning:[/bold] {message}[/cyan]")


def debug_message(message):
    console.log(message)


def exception_message(message):
    console.log(f"[blue][bold]Exception:[/bold] {message}[/blue]")

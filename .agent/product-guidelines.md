# Product Guidelines

## Tone & Voice
- **Professional & Concise:** Instructions are clear and direct, respecting the user's time and expertise.
- **Helpful & Encouraging:** Provides hints and context to assist users in making informed choices during scaffolding.
- **Transparent:** Clearly communicates the tool's actions at every step, ensuring the user is never left wondering about the current operation.

## UI & Visual Design (CLI)
- **Structured Clarity:** Information is organized using panels, tables, and nested structures to make complex configurations easy to digest.
- **Visual Feedback:** Employs a consistent color language (e.g., green for success, blue for info, red for errors) to provide immediate status recognition.
- **Progress Visualization:** Uses spinners and progress bars for time-intensive tasks to maintain engagement and indicate activity.

## Internal Code Quality
- **Strict Typing:** All internal code must utilize comprehensive type hints, ensuring robustness and facilitating automated type checking.

## User Interaction Flow
- **Logical Grouping:** Questions are sequenced logically by domain (e.g., App Settings -> Database -> Auth) to maintain mental context.
- **Sensible Defaults:** Prompts prioritize the most common or recommended options as defaults to streamline the setup process.
- **Inline Help:** Offers brief descriptions or supplemental info within prompts to clarify complex architectural or dependency choices.

## Template Scaffolding Principles
- **Zero-Configuration Start:** Generated projects are designed to be runnable immediately after scaffolding with minimal manual setup.
- **Clean & Readable Code:** Templates focus on simplicity and maintainability, providing a solid foundation without excessive boilerplate.

import json
from typing import Callable, Optional

from hide.client.hide_client import HideClient, Project
from hide.model import FileUpdateType, OverwriteUpdate, UdiffUpdate


class Toolkit:
    def __init__(self, project: Project, client: HideClient) -> None:
        self.project = project
        self.client = client

    def get_tools(self) -> list[Callable[..., str]]:
        def get_tasks() -> str:
            """Get the available tasks and their aliases in the project."""
            try:
                tasks = self.client.get_tasks(self.project.id)
                return json.dumps([task.model_dump() for task in tasks])
            except Exception as e:
                return f"Failed to get tasks: {e}"

        def run_task(command: Optional[str] = None, alias: Optional[str] = None) -> str:
            """
            Run a task in the project. Provide either command or alias. Command will be executed in the shell.
            For the list of available tasks and their aliases, use the `get_tasks` tool.
            """
            try:
                result = self.client.run_task(
                    project_id=self.project.id, command=command, alias=alias
                )
                return f"exit code: {result.exit_code}\nstdout: {result.stdout}\nstderr: {result.stderr}"
            except Exception as e:
                return f"Failed to run task: {e}"

        def create_file(path: str, content: str) -> str:
            """Create a file in the project."""
            try:
                file = self.client.create_file(
                    project_id=self.project.id, path=path, content=content
                )
                return f"File created: {file.path}\n{file}"
            except Exception as e:
                return f"Failed to create file: {e}"

        def apply_patch(path: str, patch: str) -> str:
            """Apply a patch to a file in the project. Patch must be in the unified diff format."""
            try:
                file = self.client.update_file(
                    project_id=self.project.id,
                    path=path,
                    update=UdiffUpdate(patch=patch),
                )
                return f"File updated: {file.path}\n{file}"
            except Exception as e:
                return f"Failed to apply patch: {e}"

        def insert_lines(path: str, start_line: int, content: str) -> str:
            """Insert lines in a project file. Lines are 1-indexed."""
            try:
                file = self.client.get_file(project_id=self.project.id, path=path)
                file = file.insert_lines(start_line, content)
                file = self.client.update_file(
                    project_id=self.project.id,
                    path=file.path,
                    update=OverwriteUpdate(content=file.content()),
                )
                return f"File updated: {file.path}\n{file}"
            except Exception as e:
                return f"Failed to insert lines: {e}"

        def replace_lines(
            path: str, start_line: int, end_line: int, content: str
        ) -> str:
            """
            Replace lines in a project file. Lines are 1-indexed.
            start_line is inclusive. end_line is exclusive.
            """
            try:
                # file = self.client.update_file(
                #     project_id=self.project.id,
                #     path=path,
                #     type=FileUpdateType.LINEDIFF,
                #     update=LineDiffUpdate(
                #         start_line=start_line, end_line=end_line, content=content
                #     ),
                # )
                file = self.client.get_file(project_id=self.project.id, path=path)
                file = file.replace_lines(start_line, end_line, content)
                file = self.client.update_file(
                    project_id=self.project.id,
                    path=file.path,
                    update=OverwriteUpdate(content=file.content()),
                )
                return f"File updated: {file.path}\n{file}"
            except Exception as e:
                return f"Failed to replace lines: {e}"

        def append_lines(path: str, content: str) -> str:
            """Append lines to a file in the project."""
            try:
                file = self.client.get_file(project_id=self.project.id, path=path)
                file = file.append_lines(content)
                file = self.client.update_file(
                    project_id=self.project.id,
                    path=file.path,
                    update=OverwriteUpdate(content=file.content()),
                )
                return f"File updated: {file.path}\n{file}"
            except Exception as e:
                return f"Failed to append lines: {e}"

        def get_file(path: str) -> str:
            """Get a file from the project."""
            try:
                file = self.client.get_file(project_id=self.project.id, path=path)
                return f"```{file.path}\n{file}```"
            except Exception as e:
                return f"Failed to get file: {e}"

        def delete_file(path: str) -> str:
            """Delete a file from the project."""
            try:
                deleted = self.client.delete_file(project_id=self.project.id, path=path)
                return (
                    f"File deleted: {path}"
                    if deleted
                    else f"Failed to delete file: {path}"
                )
            except Exception as e:
                return f"Failed to delete file: {e}"

        def list_files() -> str:
            """List files in the project."""
            try:
                files = self.client.list_files(project_id=self.project.id)
                return "\n".join([file.path for file in files])
            except Exception as e:
                return f"Failed to list files: {e}"

        return [
            append_lines,
            apply_patch,
            create_file,
            delete_file,
            get_file,
            get_tasks,
            insert_lines,
            list_files,
            replace_lines,
            run_task,
        ]

    def as_langchain(self) -> "LangchainToolkit":
        from hide.langchain.toolkit import LangchainToolkit

        return LangchainToolkit(toolkit=self)

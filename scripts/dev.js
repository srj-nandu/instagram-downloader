import { spawn } from "node:child_process";

const repoRoot = process.cwd();
const isWindows = process.platform === "win32";
const npmCommand = isWindows ? "npm.cmd" : "npm";

function startProcess(name, command, args, cwd) {
  const child = spawn(command, args, {
    cwd,
    stdio: "inherit",
    shell: isWindows && command.toLowerCase().endsWith(".cmd")
  });

  child.on("exit", (code, signal) => {
    if (shuttingDown) {
      return;
    }

    const reason = signal ? `signal ${signal}` : `code ${code ?? 0}`;
    console.error(`${name} exited with ${reason}.`);
    shutdown(code ?? 1);
  });

  child.on("error", (error) => {
    if (shuttingDown) {
      return;
    }

    console.error(`${name} failed to start: ${error.message}`);
    shutdown(1);
  });

  return child;
}

const children = [];
let shuttingDown = false;

function shutdown(exitCode = 0) {
  if (shuttingDown) {
    return;
  }

  shuttingDown = true;

  for (const child of children) {
    if (child.exitCode === null) {
      child.kill("SIGTERM");
    }
  }

  setTimeout(() => {
    process.exit(exitCode);
  }, 300);
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));

children.push(
  startProcess("client", npmCommand, ["--prefix", "client", "run", "dev"], repoRoot)
);
children.push(
  startProcess("server", npmCommand, ["--prefix", "server", "run", "dev"], repoRoot)
);

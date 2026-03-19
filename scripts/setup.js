import { copyFileSync, existsSync } from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const repoRoot = process.cwd();
const isWindows = process.platform === "win32";
const npmCommand = isWindows ? "npm.cmd" : "npm";

function run(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      stdio: "inherit",
      shell: isWindows && command.toLowerCase().endsWith(".cmd")
    });

    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${command} ${args.join(" ")} exited with code ${code}`));
    });

    child.on("error", (error) => {
      reject(error);
    });
  });
}

function ensureEnvFile(servicePath) {
  const envPath = path.join(servicePath, ".env");
  const examplePath = path.join(servicePath, ".env.example");

  if (!existsSync(envPath) && existsSync(examplePath)) {
    copyFileSync(examplePath, envPath);
    console.log(`Created ${path.relative(repoRoot, envPath)} from .env.example`);
  }
}

async function main() {
  console.log("Installing frontend dependencies...");
  await run(npmCommand, ["install"], path.join(repoRoot, "client"));

  console.log("Installing backend dependencies...");
  await run(npmCommand, ["install"], path.join(repoRoot, "server"));

  ensureEnvFile(path.join(repoRoot, "client"));
  ensureEnvFile(path.join(repoRoot, "server"));

  console.log("");
  console.log("Setup complete.");
  console.log("Next step: npm run dev");
}

main().catch((error) => {
  console.error(`Setup failed: ${error.message}`);
  process.exit(1);
});

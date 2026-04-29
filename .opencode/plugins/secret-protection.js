const SECRET_PATH_PATTERN = /(^|\/)(\.env(\..*)?|credentials\.json)$|(^|\/)(secrets?|credentials)(\/|$)|\.(pem|key|p12|pfx|crt|cer)$/i

export const SecretProtection = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "read") return

      const filePath = output?.args?.filePath || output?.args?.path || ""
      if (SECRET_PATH_PATTERN.test(filePath)) {
        throw new Error(`Blocked secret-like file read: ${filePath}`)
      }
    },
  }
}

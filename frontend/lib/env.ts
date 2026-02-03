export const getRequiredEnv = (key: string): string => {
  const value = process.env[key];

  if (!value) {
    throw new Error(
      `Environment variable ${key} is required but was not provided.`,
    );
  }

  return value;
};

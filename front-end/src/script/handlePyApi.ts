export const handlePyApi = async (
  operation: () => Promise<any>,
  error: (error: string) => void
): Promise<any> => {
  try {
    const result = await operation();
    return result;
  } catch (err) {
    const key_word = "Cannot read properties of undefined (reading 'api')";
    if (err instanceof TypeError && err.message.includes(key_word)) {
      error(`Pywebview API is not available. Please ensure the Pywebview backend is running.`);
    } else {
      throw err; // Re-throw the error if it's not the expected type
    }
  }
};

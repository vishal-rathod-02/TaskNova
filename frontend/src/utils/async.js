/**
 * Guarantees a minimum visual duration for loading spinners and skeleton animations
 * so fast local/cached responses don't result in jarring 5ms flashes.
 *
 * @param {Promise|Function} action - Async action or promise to execute
 * @param {number} minMs - Minimum duration in milliseconds (default: 1800ms)
 * @returns {Promise<any>} Result of the action
 */
export async function withMinLoading(action, minMs = 1800) {
  const start = Date.now();
  const promise = typeof action === "function" ? action() : action;

  try {
    const result = await promise;
    const elapsed = Date.now() - start;
    if (elapsed < minMs) {
      await new Promise((resolve) => setTimeout(resolve, minMs - elapsed));
    }
    return result;
  } catch (err) {
    const elapsed = Date.now() - start;
    if (elapsed < minMs) {
      await new Promise((resolve) => setTimeout(resolve, minMs - elapsed));
    }
    throw err;
  }
}

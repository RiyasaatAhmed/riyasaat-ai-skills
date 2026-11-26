// expect:
export function remember(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {} // ui-states-ignore: storage can be full or blocked, and the app works without it
}

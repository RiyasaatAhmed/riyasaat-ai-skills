// expect: swallowed-error, failure-as-empty
export function SaveSettings({ settings }) {
  async function save() {
    try {
      const res = await fetch('/api/settings', { method: 'POST', body: JSON.stringify(settings) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
    } catch (e) {
      console.error(e);
    }
  }

  const loadPresets = () => fetch('/api/presets').then((r) => r.json()).catch(() => []);

  return <button onClick={save}>Save</button>;
}

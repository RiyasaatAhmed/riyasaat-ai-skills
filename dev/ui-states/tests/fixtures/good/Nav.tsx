// expect:
const links = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
];

export function Nav() {
  return (
    <nav>
      {links.map((link) => <a key={link.href} href={link.href}>{link.label}</a>)}
    </nav>
  );
}

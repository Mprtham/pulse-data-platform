import './PulseIndicator.css';

export default function PulseIndicator({ active = true }) {
  return (
    <span className={`pulse-wrap ${active ? 'pulse-active' : 'pulse-inactive'}`}>
      <span className="pulse-ring" />
      <span className="pulse-dot" />
    </span>
  );
}

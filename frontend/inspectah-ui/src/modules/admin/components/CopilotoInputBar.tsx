import { FormEvent } from 'react';
import Button from '../../../shared/components/Button';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

function CopilotoInputBar({ value, onChange, onSend, disabled }: Props) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSend();
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        className="flex-1 rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:border-sky-400 focus:outline-none"
        placeholder="Peça sugestões ao Copiloto..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />
      <Button type="submit" disabled={disabled}>
        Enviar
      </Button>
    </form>
  );
}

export default CopilotoInputBar;

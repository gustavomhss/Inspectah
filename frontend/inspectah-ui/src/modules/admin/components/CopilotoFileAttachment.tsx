import { useRef } from 'react';
import type { ChangeEvent } from 'react';
import Button from '../../../shared/components/Button';
import type { CopilotoFileInfo } from '../api/copilotoClient';

interface Props {
  onAttach: (file: globalThis.File) => Promise<void>;
  attachedFiles: CopilotoFileInfo[];
  disabled?: boolean;
}

function CopilotoFileAttachment({ onAttach, attachedFiles, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await onAttach(file);
    event.target.value = '';
  };

  return (
    <div className="flex flex-col gap-2">
      <input ref={inputRef} type="file" className="hidden" onChange={handleChange} disabled={disabled} />
      <Button type="button" variant="secondary" disabled={disabled} onClick={handleClick}>
        Anexar arquivo
      </Button>
      {attachedFiles.length ? (
        <div className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200">
          <div className="mb-1 font-semibold text-white">Anexos</div>
          <ul className="space-y-1">
            {attachedFiles.map((file) => (
              <li key={file.file_id}>{file.filename}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export default CopilotoFileAttachment;

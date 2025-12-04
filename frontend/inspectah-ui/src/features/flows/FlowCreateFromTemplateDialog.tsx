import { useEffect, useState } from 'react';
import { Banner, Button, Input, Select } from '@/ui/admin';
import { useCreateFlow, useFlowTemplates } from './hooks';
import type { FlowTemplate } from './types';

interface Props {
  onCreated?: (flowId: string) => void;
}

export function FlowCreateFromTemplateDialog({ onCreated }: Props) {
  const templates = useFlowTemplates();
  const [templateSlug, setTemplateSlug] = useState<string>('');
  const [nome, setNome] = useState('');
  const [slug, setSlug] = useState('');
  const [bindingClassifier, setBindingClassifier] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { create, saving } = useCreateFlow((flow) => {
    onCreated?.(flow.id);
  });

  useEffect(() => {
    if (!templateSlug && templates.length > 0) {
      setTemplateSlug(templates[0].slug);
    }
  }, [templates, templateSlug]);

  const templateOptions = templates.filter((t: FlowTemplate) => t.ativo !== false);

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-base font-semibold">Criar fluxo a partir de template</h3>
      {error && <Banner tone="danger" title="Erro ao criar fluxo" description={error} />}
      <label className="flex flex-col gap-1" htmlFor="flow-template">
        <span className="text-sm text-slate-700">Template</span>
        <Select id="flow-template" value={templateSlug} onChange={(event) => setTemplateSlug(event.target.value)}>
          {templateOptions.map((tpl) => (
            <option key={tpl.slug} value={tpl.slug}>
              {tpl.slug} v{tpl.versao}
            </option>
          ))}
        </Select>
      </label>
      <label className="flex flex-col gap-1" htmlFor="flow-nome">
        <span className="text-sm text-slate-700">Nome</span>
        <Input id="flow-nome" value={nome} onChange={(event) => setNome(event.target.value)} placeholder="Fluxo Notícias Geral" />
      </label>
      <label className="flex flex-col gap-1" htmlFor="flow-slug">
        <span className="text-sm text-slate-700">Slug</span>
        <Input id="flow-slug" value={slug} onChange={(event) => setSlug(event.target.value)} placeholder="fluxo_noticias_geral" />
      </label>
      <label className="flex flex-col gap-1" htmlFor="flow-classifier">
        <span className="text-sm text-slate-700">Agente classificador</span>
        <Input
          id="flow-classifier"
          value={bindingClassifier}
          onChange={(event) => setBindingClassifier(event.target.value)}
          placeholder="agent_classifier_v1"
        />
      </label>
      <div className="flex justify-end">
        <Button
          onClick={() => {
            if (!templateSlug || !nome || !slug) {
              setError('Preencha template, nome e slug.');
              return;
            }
            setError(null);
            void create({
              template_slug: templateSlug,
              nome,
              slug,
              bindings: bindingClassifier ? { classificador: bindingClassifier } : {},
            }).catch((err) => setError(err instanceof Error ? err.message : 'Falha ao criar fluxo'));
          }}
          disabled={saving}
        >
          {saving ? 'Criando...' : 'Criar fluxo'}
        </Button>
      </div>
    </div>
  );
}

export default FlowCreateFromTemplateDialog;

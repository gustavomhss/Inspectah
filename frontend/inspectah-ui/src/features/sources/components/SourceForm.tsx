import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from 'react';
import { Banner, Button, FormField, Input, Select } from '@/ui/admin';
import type { SourceStatus } from '../types/Source';

export interface SourceFormValues {
  slug: string;
  name: string;
  type: string;
  category: string;
  description?: string;
  endpoint?: string;
  state?: SourceStatus;
  themes?: string[];
  info_types?: string[];
  refresh_interval?: number | null;
}

interface SourceFormProps {
  initialValues?: SourceFormValues;
  submitting?: boolean;
  showStateField?: boolean;
  onSubmit?: (values: SourceFormValues) => void;
}

const defaultValues: SourceFormValues = {
  slug: '',
  name: '',
  type: 'news_rss',
  category: 'general',
  description: '',
  endpoint: '',
  state: 'PROPOSED',
  themes: [],
  info_types: [],
  refresh_interval: 1440,
};

const sourceTypes = [
  { value: 'news_rss', label: 'RSS de notícias' },
  { value: 'official_open', label: 'Fonte oficial' },
  { value: 'data_api', label: 'API de dados' },
  { value: 'static_dataset', label: 'Dataset estático' },
];

const sourceStates: SourceStatus[] = ['PROPOSED', 'TESTING', 'ACTIVE', 'UNDER_REVIEW', 'SUSPECT', 'DISABLED_TEMP', 'DISABLED_PERM'];

function slugify(text: string): string {
  return text
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '')
    .trim();
}

export function SourceForm({ initialValues, submitting = false, showStateField = false, onSubmit }: SourceFormProps) {
  const [values, setValues] = useState<SourceFormValues>(initialValues ?? defaultValues);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    setValues(initialValues ?? defaultValues);
  }, [initialValues]);

  const slugPlaceholder = useMemo(() => slugify(values.name || 'nova-fonte'), [values.name]);

  const handleChange = (key: keyof SourceFormValues) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const value = event.target.value;
    setValues((current) => {
      if (key === 'name' && (!current.slug || current.slug === slugify(current.name))) {
        return { ...current, name: value, slug: slugify(value) };
      }
      if (key === 'themes' || key === 'info_types') {
        return { ...current, [key]: value.split(',').map((item) => item.trim()).filter(Boolean) };
      }
      if (key === 'refresh_interval') {
        const numeric = value ? Number(value) : null;
        return { ...current, refresh_interval: Number.isNaN(numeric) ? null : numeric };
      }
      return { ...current, [key]: value };
    });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!values.name.trim() || !values.slug.trim() || !values.type.trim() || !values.category.trim()) {
      setFormError('Preencha pelo menos nome, slug, tipo e categoria da fonte.');
      return;
    }
    setFormError(null);
    onSubmit?.({ ...values, slug: values.slug.trim(), name: values.name.trim() });
  };

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
      <Banner
        tone="info"
        title="Console de Fontes v2"
        description="Cadastro e edição de fontes alinhados ao Design System Admin v1. Campos essenciais estão destacados."
      />

      {formError && <Banner tone="danger" title="Validação" description={formError} />}

      <FormField label="Nome da fonte" required>
        <Input
          name="name"
          value={values.name}
          onChange={handleChange('name')}
          placeholder="Ex.: Agência Oficial de Notícias"
          required
        />
      </FormField>

      <FormField label="Slug" description="Identificador único, usado nas rotas e configs" required>
        <Input
          name="slug"
          value={values.slug}
          onChange={handleChange('slug')}
          placeholder={slugPlaceholder}
          required
        />
      </FormField>

      <FormField label="Tipo" description="Define defaults de ingestão e validações">
        <Select name="type" value={values.type} onChange={handleChange('type')}>
          {sourceTypes.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
          <option value="other">Outro</option>
        </Select>
      </FormField>

      <FormField label="Categoria" description="Categoria ou taxonomia principal" required>
        <Input name="category" value={values.category} onChange={handleChange('category')} placeholder="governamental, mercado, etc." required />
      </FormField>

      {showStateField && (
        <FormField label="Estado" description="Estado operacional da fonte">
          <Select name="state" value={values.state} onChange={handleChange('state')}>
            {sourceStates.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </Select>
        </FormField>
      )}

      <FormField label="Endpoint" description="URL, caminho ou identificador principal da fonte">
        <Input
          name="endpoint"
          value={values.endpoint}
          onChange={handleChange('endpoint')}
          placeholder="https://api.exemplo.com/fontes"
        />
      </FormField>

      <FormField label="Temas" description="Lista separada por vírgula">
        <Input
          name="themes"
          value={(values.themes || []).join(', ')}
          onChange={handleChange('themes')}
          placeholder="politica, economia, clima"
        />
      </FormField>

      <FormField label="Tipos de informação" description="Lista separada por vírgula">
        <Input
          name="info_types"
          value={(values.info_types || []).join(', ')}
          onChange={handleChange('info_types')}
          placeholder="noticia, dado_estruturado"
        />
      </FormField>

      <FormField label="Intervalo de atualização (min)" description="Mínimo 15, máximo 10080 (7 dias)">
        <Input
          name="refresh_interval"
          type="number"
          min={15}
          max={10080}
          value={values.refresh_interval ?? ''}
          onChange={handleChange('refresh_interval')}
          placeholder="1440"
        />
      </FormField>

      <FormField label="Descrição">
        <Input
          name="description"
          value={values.description}
          onChange={handleChange('description')}
          placeholder="Uso, restrições ou observações."
        />
      </FormField>

      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Salvando...' : 'Salvar'}
        </Button>
      </div>
    </form>
  );
}

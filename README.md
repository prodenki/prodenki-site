# Site ProDenki (PT · EN · ES)

Site estático, sem base de dados nem plugins: 37 páginas geradas a partir de ficheiros de conteúdo.

## Publicar no Netlify (onde o prodenki.pt já está)

1. Entre em app.netlify.com e abra o site do prodenki.pt.
2. Separador **Deploys** → arraste a pasta **`dist`** para a zona "Drag and drop your site output folder here".
3. Pronto: o domínio continua o mesmo. Depois, na Google Search Console, submeta `https://prodenki.pt/sitemap.xml`.

## Antes de publicar, preencha (ficheiro `content/config.py`)

| Campo | Para quê |
|---|---|
| `phone`, `whatsapp` | Mostra telefone no topo, botões flutuantes de chamada/WhatsApp e extensão de chamada nos anúncios |
| `street`, `postal_code`, `city`, `region` | Morada no rodapé e nos dados para o Google (aparecer no mapa) |
| `linkedin`, `facebook`, `instagram` | Ícones das redes sociais no rodapé |
| `ga4_id` ou `gtm_id`, `meta_pixel_id` | Medição de conversões; o aviso de cookies só aparece quando houver um destes |

Depois de editar, gere de novo o site:

```
python3 build.py
```

## Onde mudar textos

- `content/strings.py` — página inicial, menus, formulário, privacidade (PT, EN, ES)
- `content/services.py` — as 8 páginas de serviço (PT, EN, ES)
- `src/assets/css/site.css` — cores e aspeto
- `src/assets/js/site.js` — interatividade

Fotos novas: coloque-as em `src/assets/img/` (versões `.jpg`, `.webp` e `-sm.webp`) e acrescente-as à lista `gallery` em `content/strings.py`.

## O formulário de orçamento

Usa o serviço Web3Forms, com uma chave criada para geral@prodenki.pt: os pedidos chegam a esse endereço.
Cada envio gera o evento `generate_lead` (Google) e `Lead` (Meta) para medir os anúncios.

## Painel de fotos (prodenki.pt/admin)

O painel (Decap CMS) edita `content/gallery.json` e guarda as fotos em `src/uploads/`.
Cada vez que publica no painel, o GitHub guarda a alteração e o Netlify gera o site de novo (1–2 min).

Configuração (uma vez):
1. Repositório GitHub com estes ficheiros; em `content/config.py`, `"github_repo": "utilizador/prodenki-site"`.
2. Netlify → Project configuration → Build & deploy → Link repository → o repositório (o `netlify.toml` já define `python3 build.py` e a pasta `dist`).
3. GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
   - Homepage URL: https://prodenki.pt
   - Authorization callback URL: https://api.netlify.com/auth/done
4. Netlify → Project configuration → Access & security → OAuth → Install provider → GitHub → Client ID e Client secret da app do passo 3.
5. Abrir https://prodenki.pt/admin → Entrar com o GitHub.

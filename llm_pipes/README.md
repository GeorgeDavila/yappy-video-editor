# LLM_pipes

### API vs Local

For most users and use cases it's probably better to offload inference and embeddings off to api inference.

# LLMs

Prefer use of near-SOTA LLMs. Defaulting to `gpt-5.6-luna-pro` on api inference and `qwen 3.X 27b` models for local inference. 

### OpenRouter APIs
* https://openrouter.ai/openai/gpt-5.6-luna-pro

# Embeddings

> [!IMPORTANT]
> Whichever embeds you use, keep embedding models consistent for each use case. 

IDK how well embeds work on openrouter. Surprisingly they only have ~37 embed models as of writing, surprisingly small compared to other models. So they may discontinue them often or not have good support. Seemingly don't have video/audio embed support 

Use `llm_pipes.embed_funnel` for local embedding inference. Local embeds was the default for me but I'll probably kick the public default to api inference to account for variable hardware. Local embedding isnt too heavy and older embeds like CLIP still perform great for lots of purposes here - that should be able to run locally on any decent post 2020 cpu. 

I'll try to go back and kick back to local inference or alternate apis where apis fail. Raise issues where i might've missed any. 

### OpenRouter APIs
> [!WARNING]
> Openrouter lacking embed support. Docs are iffy at best and small selection of embeds. Doesn't seem to be any native audio/video embeds or multimodal embeds that include these. Use with caution. 

* https://openrouter.ai/docs/api_reference/embeddings
* https://developers.openai.com/api/docs/guides/embeddings
* https://openrouter.ai/docs/guides/overview/multimodal/image-understanding
* https://openrouter.ai/docs/api/api-reference/embeddings/submit-an-embedding-request
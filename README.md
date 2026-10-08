# Nano Banana for Dify: step-by-step guide

Generate one Nano Banana image from a prompt. This guide takes you from your first API key to the result in a Dify Workflow. Screenshots use Dify CE 1.17.1 in English; later versions may move the same controls.

[Read in Simplified Chinese](https://github.com/AceDataCloud/NanoBananaDify/blob/main/readme/README_zh_Hans.md) · [API and pricing](https://platform.acedata.cloud/models)

> **Publication pending:** the earlier 0.0.1 submission was merged, but its Marketplace upload failed. This 0.0.2 tutorial update is a new submission, not proof of publication. Follow [release issue #3247](https://github.com/langgenius/dify-plugins/issues/3247). The Nano screenshots show a real development preview and previously successful API task, not a Marketplace installation.

## 1. Install the correct plugin

Open [Nano Banana by acedatacloud](https://marketplace.dify.ai/plugin/acedatacloud/nano-banana) in Dify Marketplace. Check the author is **acedatacloud**, choose **Install**, and select your Dify workspace. If it is not listed yet, wait for publication; do not use another similarly named plugin for these steps.

If your Dify server cannot open Marketplace, ask its administrator to enable outbound access and plugin installation. The plugin needs HTTPS to `api.acedata.cloud`.

## 2. Get an API key with the correct access

1. Sign in at [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications).
2. Open **General application**. Its API key can access multiple services your account is entitled to use. A service-specific key is limited to that service. For this tutorial, check **Nano Banana** access and current pricing/balance before generating.
3. To reuse the selected key, click the copy icon marked **1** below. To create a separate Dify key, click **Manage Keys** marked **2**, then **Create**.

![Copy an existing API key or open Manage Keys](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/get-api-key-en.png)

4. Give the new key a name, such as `Dify tutorial`. Set expiration and usage/API restrictions only as needed, then click **Create**. Return to the key list or application card and copy the key. If **Allowed APIs** is enabled, include both the generation and task-query APIs used here: `/nano-banana/images`, `/nano-banana/tasks`.

![Create an optional separate key](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/create-api-key-en.png)

Copy only the token string. Do not add `Bearer `, quotation marks, or the screenshot's redacted characters. A platform management token (for example, a `platform-...` token) is not the generation API key this plugin expects. Free quota and model entitlement are not guaranteed.

## 3. Authorize Nano Banana in Dify

1. Open **Integrations → Tools → Tool Plugin → Nano Banana**.
2. Click **API Key Authorization Configuration**. If an authorization already exists, click **1 Authorization** first, then the configuration button.
3. Enter an **Authorization Name**, such as `Ace Data Cloud`, and paste the copied token into **Ace Data Cloud Bearer Token**.
4. Choose who may use the credential and click **Save**. The screenshot shows the shared tool-authorization dialog; GPT Image is the pictured example. Never put a key in a prompt or workflow export.

![Dify tool authorization dialog](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/02-authorize.png)

## 4. Build your first Workflow

Open **Studio → Create from Blank → Workflow**, name it, and create this path by dragging from each node's right connector to the next node:

**Start → Nano Banana Generate Image → Nano Banana Retrieve Task → Output**.

Use the **+** button to add a **Tool**, select this plugin, and choose the exact action above. Rename the generation node **Nano Banana** and the query node **Retrieve completed task** to match the screenshots. Leave Start inputs empty for this fixed first example. Keep **Retry on Failure** off on the generation node.

![Workflow connections](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/03-workflow.png)

Select **Nano Banana Generate Image** and set these fields. Leave unmentioned optional fields empty.

| Dify field | First-run value |
|---|---|
| Model (`model`) | `nano-banana-2-lite` |
| Resolution (`resolution`) | `1K` |
| Aspect ratio (`aspect_ratio`) | `1:1` |
| Image count (`count`) | `1` |

**Prompt** (`prompt`):

```text
A single teal ceramic cube on a plain cream background, studio product photograph, no text.
```

For editing, select **Nano Banana Edit Image**, set **Reference image URLs** to a JSON array such as `["https://your-domain.example/input.png"]`, and describe the change. Replace the placeholder URL with your own accessible image. Model variants have separate access and pricing.

![Fill the generation or search parameters](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/03-configure.png)

## 5. Wait for the same task and map the result

Select **Nano Banana Retrieve Task**. In **Task ID**, click the variable picker (or type `/`) and choose **Nano Banana → task_id**. It must be the output variable from the generation node, not its name typed as plain text. The DSL representation is `{{#generate.task_id#}}`. Set **Wait up to seconds** to `240`; leave Trace ID empty for this example.

![Task ID variable binding](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/04-task-id.png)

Select **Output**, click **+** to add output fields, and choose the variables below from **Retrieve completed task**:

| Output name | Select from query node | Type |
|---|---|---|
| status | status | String |
| success | success | Boolean |
| task_id | task_id | String |
| media_urls | media_urls | Array[String] |
| result | result | Object |

![Map the query outputs](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/05-output.png)

Click **Test Run → Start Run**. Generation may finish before the bounded wait expires; otherwise `status=pending` is normal. **Do not rerun the whole workflow while it is pending**, because that submits a new generation. Copy its task ID and create a separate **Start → Nano Banana Retrieve Task → Output** workflow with that ID and a wait of 0 or 240. Query the same ID until `status=succeeded` and `success=true`; then open the links in `media_urls`. A green Dify workflow alone is not proof that the service task finished.

## 6. Check the expected output

A completed result has this shape (the URL below illustrates the field; use your own returned URL):

```json
{
  "status": "succeeded",
  "success": true,
  "media_urls": [
    "https://.../result.png"
  ]
}
```

![Actual completed Dify result](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/a89b011ba7f9ca5d9dab40ab8b93d258181e0031/_assets/tutorial/06-result.png)

This is a real previously successful run, reused for the guide without another paid generation. Nano was tested through Dify developer preview; it does not prove Marketplace publication. Your task ID and media URL will differ.

## Troubleshooting

| What you see | What to do |
|---|---|
| Authorization fails / 401 or 403 | Copy the full API token, remove `Bearer `, check service access, balance, expiration and Allowed APIs. |
| Invalid parameter / 400 | Copy the exact example model, action, resolution and JSON shape. Do not combine unrelated action fields. |
| `pending` or an empty media list | Query the same task ID again. Never regenerate just to poll. |
| HTTP 429 | Wait, reduce concurrency and check service limits; do not enable automatic paid retries. |
| Timeout / 5xx / failed task | Inspect the original task or request history before resubmitting. Contact support with task/trace ID, never your key. |
| Media link will not load | Check the task is terminal and the returned link is accessible from the Dify server/browser. |

## Privacy, cost and support

The free plugin sends your chosen inputs and token to `api.acedata.cloud`; API calls follow current service pricing. Keys stay in Dify credential storage. See [Privacy](https://github.com/AceDataCloud/NanoBananaDify/blob/main/PRIVACY.md). Only submit content you have permission to process.

[Source](https://github.com/AceDataCloud/NanoBananaDify) · [Report a problem](https://github.com/AceDataCloud/NanoBananaDify/issues) · dev@acedata.cloud · [Advanced capabilities](https://github.com/AceDataCloud/NanoBananaDify/blob/main/CAPABILITIES.md). Development and test evidence live in the source repository, separate from this first-run guide.

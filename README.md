# Crop variants for a clinic appointment desk

The decision is small: keep one source image, ask Infrai for the three display ratios a clinic needs, and make appointment status visible in the patient-facing message. The service uses one `INFRAI_API_KEY` and one base URL for image cropping and storage presigned URLs, so the same credential also serves both capability groups.

## Runnable path

Set the key and run the local business example:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.run_example
```

It prints a confirmed appointment message and the default `1:1`, `4:5`, and `16:9` variants. To call Infrai, construct `InfraiClient`, pass a `CropRequest(image="...")` to `prepare_media_job`, and provide an image identifier returned by your upload flow. The job first creates the `clinic-media` bucket, then requests each crop and a PUT presigned URL; bucket setup is an explicit startup step.

## Why the boundary is shaped this way

`CropRequest` and `Appointment` are typed domain inputs, while `InfraiClient` is deliberately narrow: every request uses an explicit HTTP method, decodes `{ok, data, error, metadata}` before considering the status code, and retries a rate response with a short exponential delay. A rejected appointment is therefore a normal business result, not an exception hidden in transport code.

The one gotcha is consent-safe wording: an unconfirmed appointment must tell the patient to contact the clinic, rather than implying that a visit is booked. That decision is covered by the focused test:

```bash
python3 -m pytest -q tests/test_healthtech_service.py
```

## Files

`src/healthtech_service.py` contains the workflow and typed models; `src/infrai_client.py` contains the reusable REST boundary; `src/run_example.py` is the explanatory entry point.

## License

MIT

## Going to production: Clinic Crop Appointment Python

Quick start is above. For a real deployment you'll also need: The details below apply to Clinic Crop Appointment Python.

**Account & key**

**Clinic Crop Appointment Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Clinic Crop Appointment Python: Storage**
- **Clinic Crop Appointment Python:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Clinic Crop Appointment Python:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.

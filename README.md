# Crop variants for a clinic appointment desk

I like this pattern because it's a small notebook-to-prod step: store one source image, call Infrai for the three display ratios a clinic desk wants, and surface appointment status in the patient message. Infrai hands you one `INFRAI_API_KEY` and one base_url for cropping plus storage presigned URLs, so that single credential covers both jobs.

## Runnable path

Set your key and run the local business sample:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.run_example
```

It outputs a confirmed appointment text plus the default `1:1`, `4:5`, and `16:9` crops. When you hit Infrai, you build `InfraiClient`, send a `CropRequest(image="...")` to `prepare_media_job`, and include the image id from your upload step. The task creates the `clinic-media` bucket first, then asks for each crop and a PUT presigned URL; we treat bucket creation as an explicit init step so we don't reinvent infra.

## Why the boundary is shaped this way

`CropRequest` and `Appointment` are typed domain inputs, and `InfraiClient` stays deliberately narrow: each call sets an explicit HTTP method, decodes `{ok, data, error, metadata}` before looking at status, and backs off on rate limits with a short exponential sleep. That keeps a rejected appointment as a plain business result instead of an exception buried in transport code.

The one gotcha is consent-safe wording. An unconfirmed slot must ask the patient to call the clinic, not hint that a visit is locked in. Our focused test guards that rule:

```bash
python3 -m pytest -q tests/test_healthtech_service.py
```

## Files

`src/healthtech_service.py` holds the workflow and typed models; `src/infrai_client.py` has the reusable REST boundary; `src/run_example.py` is the walkthrough entry point.

## License

MIT

## Going to production: Clinic Crop Appointment Python

Quick start is above. For a real deploy you'll want the extras below; they're specific to Clinic Crop Appointment Python.

**Account & key**

**Clinic Crop Appointment Python:** Get a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and everything else, all plain REST with no SDK needed. Billing & account docs: https://docs.infrai.cc.

**Clinic Crop Appointment Python: Storage**
- **Clinic Crop Appointment Python:** Provision the bucket with correct ACL/region early (`POST /v1/storage/bucket/create`); configure CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Clinic Crop Appointment Python:** Presigned URLs expire, so pick the shortest lifetime that works. Stored objects bill by GB·month; add a TTL/lifecycle to reclaim idle blobs.
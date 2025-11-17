import csv
import argparse
import time
import requests
from ollama import Client

def fetch_cve_from_circl(cve_id):
    url = f"https://cve.circl.lu/api/cve/{cve_id}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        desc = data.get("containers", {}).get("cna", {}).get("descriptions", [])
        if not desc:
            return None
        return desc[0].get("value", "")
    except:
        return None

def summarize_with_ollama(model, text):
    try:
        client = Client()
        prompt = f"CVE脆弱性説明:\n{text}\n\n非専門家でも理解できるように、対策方法を簡潔に日本語で説明してください。"
        response = client.generate(model=model, prompt=prompt)
        return response["response"]
    except Exception as e:
        return f"AI_ERROR: {str(e)}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r") as f:
        cve_list = [line.strip() for line in f if line.strip()]

    with open(args.output, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["cve_id", "ai_output"])

        for idx, cve_id in enumerate(cve_list, 1):
            print(f"[{idx}/{len(cve_list)}] {cve_id} を処理中...")

            text = fetch_cve_from_circl(cve_id)
            if not text:
                writer.writerow([cve_id, "説明取得失敗"])
                continue

            result = summarize_with_ollama("phi3:mini", text)
            writer.writerow([cve_id, result])

            time.sleep(1)

    print("完了しました。")

if __name__ == "__main__":
    main()


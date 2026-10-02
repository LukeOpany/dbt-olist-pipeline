import argparse
import hashlib
import json
from pathlib import Path
from delivery.analysis import build_orders, memo, summarize, seller_summary

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',required=True)
    parser.add_argument('--output',default='reports')
    parser.add_argument('--source-url',required=True)
    args=parser.parse_args()
    frame,sellers=build_orders(args.data_dir)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/'delivery-findings.md').write_text(memo(frame,sellers))
    summarize(frame,'customer_state').to_csv(out/'delivery-by-state.csv',index=False)
    seller_summary(frame,sellers).to_csv(out/'delivery-by-seller.csv',index=False)
    provenance={'source_url':args.source_url,'source_rows':len(frame),'eligible_orders':int(frame.eligible.sum()),
                'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(args.data_dir).glob('olist_*.csv'))}}
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print((out/'delivery-findings.md').read_text())

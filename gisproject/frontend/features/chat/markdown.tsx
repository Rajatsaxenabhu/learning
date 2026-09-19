import type { Components } from 'react-markdown'

export const mdComponents: Components = {
  p: (props) => <p className="my-2 first:mt-0 last:mb-0" {...props} />,
  ul: (props) => <ul className="my-2 list-disc space-y-1 pl-5" {...props} />,
  ol: (props) => <ol className="my-2 list-decimal space-y-1 pl-5" {...props} />,
  strong: (props) => <strong className="font-semibold" {...props} />,
  code: (props) => <code className="rounded-md bg-foreground/10 px-1.5 py-0.5 font-mono text-[13px]" {...props} />,
  pre: (props) => <pre className="my-3 overflow-auto rounded-xl bg-foreground/[0.06] p-4 text-[13px]" {...props} />,
  a: (props) => <a className="text-emerald-400 underline underline-offset-2" target="_blank" rel="noreferrer" {...props} />,
}

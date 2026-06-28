const { Layers } = LucideReact;

export function DuplicatesSection({ theme }) {
  return (
                 <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-10 shadow-2xl animate-in zoom-in-95 duration-500`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                      <div>
                        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${theme.textPrimary}`}>
                          <Layers className="text-blue-500" /> Duplicate Rows
                        </h2>
                        <p className={`${theme.textSub} text-sm`}>
                          Records that are exactly identical across all variables.
                        </p>
                      </div>
                    </div>
                    <div className={`py-12 text-center ${theme.textSub} border ${theme.borderAlt} border-dashed rounded-xl`}>
                      Duplicate data overview not available in current payload.
                    </div>
                 </div>
  );
}

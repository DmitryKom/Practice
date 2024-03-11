# Makefile для сборки ВКР.
# Автор: Шмаков И.А.
# Версия: 27.12.2021

default: help
.PHONY: default

report:
	xelatex -shell-escape main-report-csae && biber main-report-csae && xelatex -shell-escape main-report-csae
.PHONY: book

clean:
	rm *.aux *.log *.bbl *.bcf *.blg *.toc *.run.xml *.out
.PHONY: clean

# Help Target
help:
	@echo "Следующие цели представлены в данном Makefile:"
	@echo "... help (Данная цель является целью по умолчанию)"
	@echo "... report сборка отчёта"
	@echo "... clean удаление временных файлов"
.PHONY: help

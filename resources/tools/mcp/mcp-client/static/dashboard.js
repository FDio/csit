document.querySelectorAll("[data-auto-submit]").forEach((control) => {
  control.addEventListener("change", () => {
    control.form.requestSubmit();
  });
});

document.querySelectorAll("[data-trending-filter]").forEach((control) => {
  control.addEventListener("change", () => {
    control.form.requestSubmit();
  });
});

document.querySelectorAll("[data-iterative-filter]").forEach((control) => {
  control.addEventListener("change", () => {
    control.form.requestSubmit();
  });
});

document.querySelectorAll(".trending-chart .chart-scroll").forEach((chart) => {
  chart.scrollLeft = chart.scrollWidth - chart.clientWidth;
});

document.querySelectorAll(".iterative-chart .chart-scroll").forEach((chart) => {
  chart.scrollLeft = 0;
});

const tooltipTargets = document.querySelectorAll(
  ".run-bar[data-tooltip], .chart-tooltip-target[data-tooltip]",
);
const runBarTargets = document.querySelectorAll(".run-bar[data-tooltip]");
let chartTooltip = null;

const hideTooltip = () => {
  if (chartTooltip) {
    chartTooltip.hidden = true;
  }
};

const fallbackCopy = (text) => {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.className = "clipboard-fallback";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) {
    throw new Error("Copy is unavailable.");
  }
};

const copyText = async (text) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }
  fallbackCopy(text);
};

const clickedOutsideDialog = (dialog, event) => {
  if (event.target !== dialog) {
    return false;
  }
  const bounds = dialog.getBoundingClientRect();
  return (
    event.clientX < bounds.left
    || event.clientX > bounds.right
    || event.clientY < bounds.top
    || event.clientY > bounds.bottom
  );
};

if (tooltipTargets.length) {
  chartTooltip = document.createElement("div");
  chartTooltip.className = "chart-tooltip";
  chartTooltip.setAttribute("role", "tooltip");
  chartTooltip.hidden = true;
  document.body.appendChild(chartTooltip);

  const positionTooltip = (event, target) => {
    const targetRect = target.getBoundingClientRect();
    const hasPointer = event && event.clientX > 0 && event.clientY > 0;
    const originX = hasPointer
      ? event.clientX
      : targetRect.left + targetRect.width / 2;
    const originY = hasPointer ? event.clientY : targetRect.top;
    const gap = 12;
    const margin = 8;
    const tooltipRect = chartTooltip.getBoundingClientRect();
    let left = originX + gap;
    let top = originY + gap;

    if (left + tooltipRect.width > window.innerWidth - margin) {
      left = originX - tooltipRect.width - gap;
    }
    if (top + tooltipRect.height > window.innerHeight - margin) {
      top = originY - tooltipRect.height - gap;
    }

    chartTooltip.style.left = `${Math.max(margin, left)}px`;
    chartTooltip.style.top = `${Math.max(margin, top)}px`;
  };

  const showTooltip = (event) => {
    const target = event.currentTarget;
    chartTooltip.textContent = target.dataset.tooltip;
    chartTooltip.hidden = false;
    positionTooltip(event, target);
  };

  tooltipTargets.forEach((target) => {
    target.addEventListener("mouseenter", showTooltip);
    target.addEventListener("mousemove", (event) => {
      if (!chartTooltip.hidden) {
        positionTooltip(event, target);
      }
    });
    target.addEventListener("mouseleave", hideTooltip);
    target.addEventListener("focus", showTooltip);
    target.addEventListener("blur", hideTooltip);
  });
}

const detailsDialog = document.querySelector("[data-run-statistics]")?.closest("dialog");

if (detailsDialog) {
  const runStatistics = detailsDialog.querySelector("[data-run-statistics]");
  const failedCount = detailsDialog.querySelector("[data-failed-count]");
  const failedStatus = detailsDialog.querySelector("[data-failed-status]");
  const failedTestsList = detailsDialog.querySelector("[data-failed-tests]");
  const closeButton = detailsDialog.querySelector("[data-dialog-close]");
  const copyRunButton = detailsDialog.querySelector("[data-copy-run-statistics]");
  const copyFailedButton = detailsDialog.querySelector("[data-copy-failed-tests]");
  const copyStatus = detailsDialog.querySelector("[data-copy-status]");
  let detailsController = null;
  let detailsRequestId = 0;
  let originatingBar = null;
  let failedTestsText = "";
  let feedbackTimer = null;

  const setFailedState = ({ count, message, tests = [], error = false }) => {
    failedCount.textContent = String(count);
    failedStatus.textContent = message;
    failedStatus.classList.toggle("details-error", error);
    failedTestsList.replaceChildren();
    tests.forEach((testId) => {
      const item = document.createElement("li");
      item.textContent = testId;
      failedTestsList.appendChild(item);
    });
    failedTestsText = tests.join("\n");
    copyFailedButton.disabled = tests.length === 0;
  };

  const loadFailedTests = async (target, requestId) => {
    const params = new URLSearchParams({
      job: target.dataset.runJob || "",
      build: target.dataset.runBuild || "",
    });
    detailsController = new AbortController();

    try {
      const response = await fetch(
        `/api/statistics/run-details?${params.toString()}`,
        { signal: detailsController.signal },
      );
      let payload;
      try {
        payload = await response.json();
      } catch (error) {
        throw new Error("The details response was not valid JSON.");
      }
      if (!response.ok || payload.error) {
        throw new Error(payload.message || "Failed tests are unavailable.");
      }
      if (requestId !== detailsRequestId || !detailsDialog.open) {
        return;
      }
      const tests = Array.isArray(payload.failed_tests)
        ? payload.failed_tests.map((value) => String(value))
        : [];
      setFailedState({
        count: payload.failed_count ?? tests.length,
        message: tests.length ? "" : "No failed tests.",
        tests,
      });
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      if (requestId !== detailsRequestId || !detailsDialog.open) {
        return;
      }
      setFailedState({
        count: target.dataset.failedCount || 0,
        message: error.message || "Failed tests are unavailable.",
        error: true,
      });
    }
  };

  const openDetails = (target) => {
    detailsRequestId += 1;
    const requestId = detailsRequestId;
    if (detailsController) {
      detailsController.abort();
    }
    originatingBar = target;
    hideTooltip();
    runStatistics.textContent = target.dataset.tooltip || "Run details unavailable.";
    setFailedState({
      count: target.dataset.failedCount || 0,
      message: "Loading failed tests...",
    });
    detailsDialog.showModal();
    loadFailedTests(target, requestId);
  };

  runBarTargets.forEach((target) => {
    target.addEventListener("click", () => openDetails(target));
    target.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openDetails(target);
      }
    });
  });

  closeButton.addEventListener("click", () => detailsDialog.close());
  detailsDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    detailsDialog.close();
  });
  detailsDialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      detailsDialog.close();
    }
  });
  detailsDialog.addEventListener("click", (event) => {
    if (event.target !== detailsDialog) {
      return;
    }
    const bounds = detailsDialog.getBoundingClientRect();
    const outside = (
      event.clientX < bounds.left
      || event.clientX > bounds.right
      || event.clientY < bounds.top
      || event.clientY > bounds.bottom
    );
    if (outside) {
      detailsDialog.close();
    }
  });
  detailsDialog.addEventListener("close", () => {
    detailsRequestId += 1;
    if (detailsController) {
      detailsController.abort();
      detailsController = null;
    }
    hideTooltip();
    const target = originatingBar;
    originatingBar = null;
    if (target) {
      window.requestAnimationFrame(() => target.focus());
    }
  });

  const announceCopy = (message) => {
    window.clearTimeout(feedbackTimer);
    copyStatus.textContent = message;
    feedbackTimer = window.setTimeout(() => {
      copyStatus.textContent = "";
    }, 1800);
  };

  copyRunButton.addEventListener("click", async () => {
    try {
      await copyText(runStatistics.textContent);
      announceCopy("Copied run statistics.");
    } catch (error) {
      announceCopy("Could not copy run statistics.");
    }
  });
  copyFailedButton.addEventListener("click", async () => {
    if (!failedTestsText) {
      return;
    }
    try {
      await copyText(failedTestsText);
      announceCopy("Copied failed tests.");
    } catch (error) {
      announceCopy("Could not copy failed tests.");
    }
  });
}

const trendingDetailsDialog = document.querySelector("#trending-details-dialog");
const trendingDetailsTargets = document.querySelectorAll(
  ".trending-details-target[data-tooltip]",
);

if (trendingDetailsDialog && trendingDetailsTargets.length) {
  const detailsContent = trendingDetailsDialog.querySelector(
    "[data-trending-details-content]",
  );
  const copyButton = trendingDetailsDialog.querySelector(
    "[data-copy-trending-details]",
  );
  const closeButton = trendingDetailsDialog.querySelector(
    "[data-trending-dialog-close]",
  );
  const copyStatus = trendingDetailsDialog.querySelector(
    "[data-trending-copy-status]",
  );
  let originatingTarget = null;
  let copyFeedbackTimer = null;

  const closeTrendingDetails = () => trendingDetailsDialog.close();
  const openTrendingDetails = (target) => {
    originatingTarget = target;
    detailsContent.textContent = target.dataset.tooltip || "Details unavailable.";
    copyStatus.textContent = "";
    hideTooltip();
    trendingDetailsDialog.showModal();
    closeButton.focus();
  };

  trendingDetailsTargets.forEach((target) => {
    target.addEventListener("click", () => openTrendingDetails(target));
    target.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openTrendingDetails(target);
      }
    });
  });

  closeButton.addEventListener("click", closeTrendingDetails);
  trendingDetailsDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeTrendingDetails();
  });
  trendingDetailsDialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeTrendingDetails();
    }
  });
  trendingDetailsDialog.addEventListener("click", (event) => {
    if (clickedOutsideDialog(trendingDetailsDialog, event)) {
      closeTrendingDetails();
    }
  });
  trendingDetailsDialog.addEventListener("close", () => {
    window.clearTimeout(copyFeedbackTimer);
    copyStatus.textContent = "";
    hideTooltip();
    const target = originatingTarget;
    originatingTarget = null;
    if (target) {
      window.requestAnimationFrame(() => target.focus());
    }
  });

  copyButton.addEventListener("click", async () => {
    window.clearTimeout(copyFeedbackTimer);
    try {
      await copyText(detailsContent.textContent);
      copyStatus.textContent = "Copied detailed information.";
    } catch (error) {
      copyStatus.textContent = "Could not copy detailed information.";
    }
    copyFeedbackTimer = window.setTimeout(() => {
      copyStatus.textContent = "";
    }, 1800);
  });
}

const iterativeDetailsDialog = document.querySelector("#iterative-details-dialog");
const iterativeDetailsTargets = document.querySelectorAll(
  ".iterative-details-target[data-tooltip]",
);

if (iterativeDetailsDialog && iterativeDetailsTargets.length) {
  const detailsContent = iterativeDetailsDialog.querySelector(
    "[data-iterative-details-content]",
  );
  const copyButton = iterativeDetailsDialog.querySelector(
    "[data-copy-iterative-details]",
  );
  const closeButton = iterativeDetailsDialog.querySelector(
    "[data-iterative-dialog-close]",
  );
  const copyStatus = iterativeDetailsDialog.querySelector(
    "[data-iterative-copy-status]",
  );
  let originatingTarget = null;
  let copyFeedbackTimer = null;

  const closeIterativeDetails = () => iterativeDetailsDialog.close();
  const openIterativeDetails = (target) => {
    originatingTarget = target;
    detailsContent.textContent = target.dataset.tooltip || "Details unavailable.";
    copyStatus.textContent = "";
    hideTooltip();
    iterativeDetailsDialog.showModal();
    closeButton.focus();
  };

  iterativeDetailsTargets.forEach((target) => {
    target.addEventListener("click", () => openIterativeDetails(target));
    target.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openIterativeDetails(target);
      }
    });
  });

  closeButton.addEventListener("click", closeIterativeDetails);
  iterativeDetailsDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeIterativeDetails();
  });
  iterativeDetailsDialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeIterativeDetails();
    }
  });
  iterativeDetailsDialog.addEventListener("click", (event) => {
    if (clickedOutsideDialog(iterativeDetailsDialog, event)) {
      closeIterativeDetails();
    }
  });
  iterativeDetailsDialog.addEventListener("close", () => {
    window.clearTimeout(copyFeedbackTimer);
    copyStatus.textContent = "";
    hideTooltip();
    const target = originatingTarget;
    originatingTarget = null;
    if (target) {
      window.requestAnimationFrame(() => target.focus());
    }
  });

  copyButton.addEventListener("click", async () => {
    window.clearTimeout(copyFeedbackTimer);
    try {
      await copyText(detailsContent.textContent);
      copyStatus.textContent = "Copied detailed information.";
    } catch (error) {
      copyStatus.textContent = "Could not copy detailed information.";
    }
    copyFeedbackTimer = window.setTimeout(() => {
      copyStatus.textContent = "";
    }, 1800);
  });
}

document.querySelectorAll("[data-open-download-dialog]").forEach((downloadButton) => {
  const downloadDialog = document.querySelector(
    downloadButton.dataset.downloadDialogTarget || "#download-dialog",
  );
  if (!downloadDialog) {
    return;
  }
  const form = downloadDialog.querySelector("[data-download-form]");
  const filenameInput = downloadDialog.querySelector("[data-download-filename]");
  const status = downloadDialog.querySelector("[data-download-status]");
  const submitButton = downloadDialog.querySelector("[data-download-submit]");
  const closeButtons = downloadDialog.querySelectorAll(
    "[data-download-close], [data-download-cancel]",
  );
  let downloadController = null;
  let downloadRequestId = 0;

  const setDownloadBusy = (busy) => {
    submitButton.disabled = busy;
    form.setAttribute("aria-busy", String(busy));
  };

  const closeDownloadDialog = () => downloadDialog.close();

  downloadButton.addEventListener("click", () => {
    filenameInput.value = downloadButton.dataset.defaultFilename || "export";
    const xlsx = form.querySelector('input[name="export-format"][value="xlsx"]');
    xlsx.checked = true;
    status.textContent = "";
    status.classList.remove("dialog-error");
    setDownloadBusy(false);
    downloadDialog.showModal();
    filenameInput.focus();
    filenameInput.select();
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeDownloadDialog);
  });
  downloadDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeDownloadDialog();
  });
  downloadDialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeDownloadDialog();
    }
  });
  downloadDialog.addEventListener("click", (event) => {
    if (clickedOutsideDialog(downloadDialog, event)) {
      closeDownloadDialog();
    }
  });
  downloadDialog.addEventListener("close", () => {
    downloadRequestId += 1;
    if (downloadController) {
      downloadController.abort();
      downloadController = null;
    }
    setDownloadBusy(false);
    window.requestAnimationFrame(() => downloadButton.focus());
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const format = form.querySelector(
      'input[name="export-format"]:checked',
    ).value;
    const rawFilename = filenameInput.value.trim()
      || downloadButton.dataset.defaultFilename
      || "export";
    const filename = `${rawFilename.replace(/\.(csv|xlsx)$/i, "")}.${format}`;
    const mimeType = format === "csv"
      ? "text/csv"
      : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
    let fileHandle = null;

    status.textContent = "Choose a destination...";
    status.classList.remove("dialog-error");
    try {
      if (typeof window.showSaveFilePicker === "function") {
        fileHandle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: format === "csv" ? "CSV file" : "Excel workbook",
            accept: { [mimeType]: [`.${format}`] },
          }],
        });
      }
    } catch (error) {
      if (error.name === "AbortError") {
        status.textContent = "";
        return;
      }
      status.textContent = error.message || "A destination could not be selected.";
      status.classList.add("dialog-error");
      return;
    }

    downloadRequestId += 1;
    const requestId = downloadRequestId;
    downloadController = new AbortController();
    setDownloadBusy(true);
    status.textContent = "Preparing export...";

    const params = new URLSearchParams(downloadButton.dataset.exportParams || "");
    params.set("format", format);
    params.set("filename", rawFilename);
    if (!downloadButton.dataset.exportParams) {
      ["dut", "testType", "cadence", "testbed"].forEach((field) => {
        const value = downloadButton.dataset[`filter${field[0].toUpperCase()}${field.slice(1)}`];
        if (value) {
          const name = field === "testType" ? "test_type" : field;
          params.set(name, value);
        }
      });
    }

    try {
      const endpoint = downloadButton.dataset.exportEndpoint
        || "/api/statistics/export";
      const response = await fetch(`${endpoint}?${params.toString()}`, {
        signal: downloadController.signal,
      });
      if (!response.ok) {
        let message = "The export could not be generated.";
        try {
          const payload = await response.json();
          message = payload.message || message;
        } catch (error) {
          // Preserve the useful generic message for non-JSON gateway failures.
        }
        throw new Error(message);
      }
      const blob = await response.blob();
      if (requestId !== downloadRequestId || !downloadDialog.open) {
        return;
      }
      if (fileHandle) {
        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
        status.textContent = `Saved ${filename}.`;
      } else {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = filename;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        status.textContent = `Downloaded ${filename}.`;
      }
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      if (requestId !== downloadRequestId || !downloadDialog.open) {
        return;
      }
      status.textContent = error.message || "The export could not be generated.";
      status.classList.add("dialog-error");
    } finally {
      if (requestId === downloadRequestId) {
        downloadController = null;
        setDownloadBusy(false);
      }
    }
  });
});

document.querySelectorAll("[data-open-url-dialog]").forEach((showUrlButton) => {
  const showUrlDialog = document.querySelector(
    showUrlButton.dataset.urlDialogTarget || "#show-url-dialog",
  );
  if (!showUrlDialog) {
    return;
  }
  const urlInput = showUrlDialog.querySelector("[data-current-page-url]");
  const copyButton = showUrlDialog.querySelector("[data-copy-url]");
  const status = showUrlDialog.querySelector("[data-url-status]");
  const closeButton = showUrlDialog.querySelector("[data-url-close]");
  let feedbackTimer = null;

  const closeUrlDialog = () => showUrlDialog.close();
  showUrlButton.addEventListener("click", () => {
    const pageUrl = new URL(window.location.href);
    if (showUrlButton.dataset.urlMode === "statistics") {
      pageUrl.searchParams.set("dataset", "statistics");
      ["dut", "testType", "cadence", "testbed"].forEach((field) => {
        const value = showUrlButton.dataset[`filter${field[0].toUpperCase()}${field.slice(1)}`];
        const name = field === "testType" ? "test_type" : field;
        if (value) {
          pageUrl.searchParams.set(name, value);
        } else {
          pageUrl.searchParams.delete(name);
        }
      });
    }
    urlInput.value = pageUrl.href;
    status.textContent = "";
    showUrlDialog.showModal();
    urlInput.focus();
    urlInput.select();
  });
  closeButton.addEventListener("click", closeUrlDialog);
  showUrlDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeUrlDialog();
  });
  showUrlDialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeUrlDialog();
    }
  });
  showUrlDialog.addEventListener("click", (event) => {
    if (clickedOutsideDialog(showUrlDialog, event)) {
      closeUrlDialog();
    }
  });
  showUrlDialog.addEventListener("close", () => {
    window.clearTimeout(feedbackTimer);
    window.requestAnimationFrame(() => showUrlButton.focus());
  });
  copyButton.addEventListener("click", async () => {
    window.clearTimeout(feedbackTimer);
    try {
      await copyText(urlInput.value);
      status.textContent = "Copied current page URL.";
    } catch (error) {
      status.textContent = "Could not copy the current page URL.";
      status.classList.add("dialog-error");
    }
    feedbackTimer = window.setTimeout(() => {
      status.textContent = "";
      status.classList.remove("dialog-error");
    }, 1800);
  });
});

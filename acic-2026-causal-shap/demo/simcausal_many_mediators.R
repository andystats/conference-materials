#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(simcausal))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
n <- if (length(args) >= 1) as.integer(args[[1]]) else 2500L
seed <- if (length(args) >= 2) as.integer(args[[2]]) else 20260506L
output_dir <- if (length(args) >= 3) args[[3]] else file.path("demo", "output")

if (is.na(n) || n <= 0) {
  stop("n must be a positive integer")
}
if (is.na(seed)) {
  stop("seed must be an integer")
}

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(seed)

# This DAG deliberately includes downstream proxy measurements that summarize
# the mediator state but have no directed path into the outcome. They are
# predictive artifacts, not causes of AcuteRisk.
D <- DAG.empty() +
  node("Age", distr = "rnorm", mean = 0, sd = 1) +
  node("BaselineSeverity", distr = "rnorm", mean = 0, sd = 1) +
  node("ChronicBurden", distr = "rnorm", mean = 0, sd = 1) +
  node("SocialRisk", distr = "rnorm", mean = 0, sd = 1) +
  node("PracticeStyle", distr = "rnorm", mean = 0, sd = 1) +
  node(
    "TreatmentIntensity",
    distr = "rnorm",
    mean = 0.45 * PracticeStyle +
      0.70 * BaselineSeverity +
      0.35 * ChronicBurden +
      0.25 * SocialRisk -
      0.10 * Age,
    sd = 0.65
  ) +
  node(
    "Inflammation",
    distr = "rnorm",
    mean = 0.65 * BaselineSeverity +
      0.45 * ChronicBurden -
      0.20 * TreatmentIntensity +
      0.15 * SocialRisk,
    sd = 0.60
  ) +
  node(
    "Coagulation",
    distr = "rnorm",
    mean = 0.60 * Inflammation +
      0.20 * ChronicBurden,
    sd = 0.55
  ) +
  node(
    "RenalStress",
    distr = "rnorm",
    mean = 0.50 * ChronicBurden +
      0.40 * Inflammation +
      0.15 * Age +
      0.20 * TreatmentIntensity,
    sd = 0.55
  ) +
  node(
    "PerfusionDeficit",
    distr = "rnorm",
    mean = 0.75 * BaselineSeverity +
      0.45 * Inflammation -
      0.25 * TreatmentIntensity,
    sd = 0.55
  ) +
  node(
    "OxygenDeficit",
    distr = "rnorm",
    mean = 0.55 * BaselineSeverity +
      0.35 * PerfusionDeficit +
      0.25 * Inflammation -
      0.40 * TreatmentIntensity,
    sd = 0.55
  ) +
  node(
    "Lactate",
    distr = "rnorm",
    mean = 0.65 * PerfusionDeficit +
      0.35 * Inflammation +
      0.25 * OxygenDeficit,
    sd = 0.50
  ) +
  node(
    "EndOrganStress",
    distr = "rnorm",
    mean = 0.45 * RenalStress +
      0.35 * Coagulation +
      0.30 * Lactate,
    sd = 0.50
  ) +
  node(
    "ShockIndexProxy",
    distr = "rnorm",
    mean = 0.90 * PerfusionDeficit +
      0.75 * Lactate +
      0.35 * OxygenDeficit,
    sd = 0.20
  ) +
  node(
    "VasopressorProxy",
    distr = "rnorm",
    mean = 0.65 * TreatmentIntensity +
      0.50 * PerfusionDeficit +
      0.45 * ShockIndexProxy,
    sd = 0.25
  ) +
  node(
    "MonitoringProxy",
    distr = "rnorm",
    mean = 0.45 * ChronicBurden +
      0.65 * EndOrganStress +
      0.35 * ShockIndexProxy,
    sd = 0.25
  ) +
  node(
    "RescueProxy",
    distr = "rnorm",
    mean = 0.60 * VasopressorProxy +
      0.35 * MonitoringProxy +
      0.45 * ShockIndexProxy,
    sd = 0.25
  ) +
  node(
    "CompositeScoreProxy",
    distr = "rnorm",
    mean = 0.55 * ShockIndexProxy +
      0.45 * EndOrganStress +
      0.40 * RescueProxy,
    sd = 0.15
  ) +
  node(
    "AcuteRisk",
    distr = "rnorm",
    mean = 1.30 * BaselineSeverity +
      0.80 * ChronicBurden +
      0.50 * SocialRisk -
      0.70 * TreatmentIntensity +
      0.75 * Inflammation +
      0.45 * Coagulation +
      0.55 * RenalStress +
      0.85 * PerfusionDeficit +
      0.55 * OxygenDeficit +
      0.70 * Lactate +
      0.65 * EndOrganStress,
    sd = 1.00
  )

D <- set.DAG(D)
dat <- sim(D, n = n)
dat$ID <- NULL

edges <- data.frame(
  from = c(
    "PracticeStyle", "BaselineSeverity", "ChronicBurden", "SocialRisk", "Age",
    "BaselineSeverity", "ChronicBurden", "TreatmentIntensity", "SocialRisk",
    "Inflammation", "ChronicBurden",
    "ChronicBurden", "Inflammation", "Age", "TreatmentIntensity",
    "BaselineSeverity", "Inflammation", "TreatmentIntensity",
    "BaselineSeverity", "PerfusionDeficit", "Inflammation", "TreatmentIntensity",
    "PerfusionDeficit", "Inflammation", "OxygenDeficit",
    "RenalStress", "Coagulation", "Lactate",
    "PerfusionDeficit", "Lactate", "OxygenDeficit",
    "TreatmentIntensity", "PerfusionDeficit", "ShockIndexProxy",
    "ChronicBurden", "EndOrganStress", "ShockIndexProxy",
    "VasopressorProxy", "MonitoringProxy", "ShockIndexProxy",
    "ShockIndexProxy", "EndOrganStress", "RescueProxy",
    "BaselineSeverity", "ChronicBurden", "SocialRisk", "TreatmentIntensity",
    "Inflammation", "Coagulation", "RenalStress", "PerfusionDeficit",
    "OxygenDeficit", "Lactate", "EndOrganStress"
  ),
  to = c(
    "TreatmentIntensity", "TreatmentIntensity", "TreatmentIntensity", "TreatmentIntensity", "TreatmentIntensity",
    "Inflammation", "Inflammation", "Inflammation", "Inflammation",
    "Coagulation", "Coagulation",
    "RenalStress", "RenalStress", "RenalStress", "RenalStress",
    "PerfusionDeficit", "PerfusionDeficit", "PerfusionDeficit",
    "OxygenDeficit", "OxygenDeficit", "OxygenDeficit", "OxygenDeficit",
    "Lactate", "Lactate", "Lactate",
    "EndOrganStress", "EndOrganStress", "EndOrganStress",
    "ShockIndexProxy", "ShockIndexProxy", "ShockIndexProxy",
    "VasopressorProxy", "VasopressorProxy", "VasopressorProxy",
    "MonitoringProxy", "MonitoringProxy", "MonitoringProxy",
    "RescueProxy", "RescueProxy", "RescueProxy",
    "CompositeScoreProxy", "CompositeScoreProxy", "CompositeScoreProxy",
    "AcuteRisk", "AcuteRisk", "AcuteRisk", "AcuteRisk",
    "AcuteRisk", "AcuteRisk", "AcuteRisk", "AcuteRisk",
    "AcuteRisk", "AcuteRisk", "AcuteRisk"
  ),
  coefficient = c(
    0.45, 0.70, 0.35, 0.25, -0.10,
    0.65, 0.45, -0.20, 0.15,
    0.60, 0.20,
    0.50, 0.40, 0.15, 0.20,
    0.75, 0.45, -0.25,
    0.55, 0.35, 0.25, -0.40,
    0.65, 0.35, 0.25,
    0.45, 0.35, 0.30,
    0.90, 0.75, 0.35,
    0.65, 0.50, 0.45,
    0.45, 0.65, 0.35,
    0.60, 0.35, 0.45,
    0.55, 0.45, 0.40,
    1.30, 0.80, 0.50, -0.70,
    0.75, 0.45, 0.55, 0.85,
    0.55, 0.70, 0.65
  ),
  stringsAsFactors = FALSE
)

roles <- data.frame(
  node = c(
    "Age", "BaselineSeverity", "ChronicBurden", "SocialRisk", "PracticeStyle",
    "TreatmentIntensity",
    "Inflammation", "Coagulation", "RenalStress", "PerfusionDeficit",
    "OxygenDeficit", "Lactate", "EndOrganStress",
    "ShockIndexProxy", "VasopressorProxy", "MonitoringProxy", "RescueProxy",
    "CompositeScoreProxy",
    "AcuteRisk"
  ),
  role = c(
    rep("Root cause", 5),
    "Treatment",
    rep("Mediator", 7),
    rep("Downstream proxy", 5),
    "Outcome"
  ),
  description = c(
    "Standardized age-like baseline variable",
    "Unobserved acuity made observed for the demo",
    "Chronic disease burden",
    "Social vulnerability",
    "Local treatment practice tendency",
    "Care intensity assigned by baseline state and practice style",
    "Inflammatory pathway",
    "Coagulation pathway",
    "Renal/endocrine stress pathway",
    "Perfusion pathway",
    "Oxygenation deficit pathway",
    "Downstream lactate mediator",
    "Multi-organ stress mediator",
    "Post-mediator vital-sign proxy with no effect on outcome",
    "Post-treatment/post-shock proxy with no effect on outcome",
    "Monitoring intensity proxy with no effect on outcome",
    "Rescue workflow proxy with no effect on outcome",
    "Composite descendant score with no effect on outcome",
    "Continuous outcome risk"
  ),
  stringsAsFactors = FALSE
)

nodes <- unique(c(edges$from, edges$to))
B <- matrix(0, nrow = length(nodes), ncol = length(nodes), dimnames = list(nodes, nodes))
for (i in seq_len(nrow(edges))) {
  B[edges$from[[i]], edges$to[[i]]] <- edges$coefficient[[i]]
}

total <- matrix(0, nrow = length(nodes), ncol = length(nodes), dimnames = list(nodes, nodes))
power <- B
for (k in seq_len(length(nodes) - 1L)) {
  total <- total + power
  power <- power %*% B
}

features <- setdiff(nodes, "AcuteRisk")
true_effects <- data.frame(
  feature = features,
  true_total_effect = as.numeric(total[features, "AcuteRisk"]),
  true_abs_total_effect = abs(as.numeric(total[features, "AcuteRisk"])),
  stringsAsFactors = FALSE
)
true_effects <- merge(true_effects, roles[, c("node", "role")], by.x = "feature", by.y = "node", all.x = TRUE)
true_effects <- true_effects[order(-true_effects$true_abs_total_effect), ]

write.csv(dat, file.path(output_dir, "simcausal_many_mediators.csv"), row.names = FALSE)
write.csv(edges, file.path(output_dir, "ground_truth_edges.csv"), row.names = FALSE)
write.csv(roles, file.path(output_dir, "node_roles.csv"), row.names = FALSE)
write.csv(true_effects, file.path(output_dir, "true_total_effects.csv"), row.names = FALSE)

manifest <- list(
  generator = "simcausal_many_mediators.R",
  n = n,
  seed = seed,
  outcome = "AcuteRisk",
  note = "Downstream proxy variables are predictive descendants but have no directed path into AcuteRisk."
)
write_json(manifest, file.path(output_dir, "dgp_manifest.json"), pretty = TRUE, auto_unbox = TRUE)

cat("Wrote simcausal demo data to ", normalizePath(output_dir, winslash = "\\", mustWork = FALSE), "\n", sep = "")
cat("Rows: ", nrow(dat), "; predictors: ", ncol(dat) - 1L, "\n", sep = "")

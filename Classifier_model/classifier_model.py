import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_curve, auc, precision_recall_fscore_support
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

np.random.seed(42)

# 1. Load data
df = pd.read_csv("matrix.csv", index_col=0)
X_raw = df.values.astype(float)
X = X_raw.T
y = np.repeat([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],
              [12,15,12,14,9,15,12,15,12,18,18,18,9,9,9,9,6,6])

print(f"Data shape: {X.shape}")

# Define organ names
organ_names = [f'Organ{i}' for i in range(1, 19)]
n_classes = len(organ_names)

# Storage for results with per-class metrics
all_results = {
    'SVM': {
        'accuracy': [], 'f1': [], 'auc_micro': [],
        'class_precision': {organ: [] for organ in organ_names},
        'class_recall': {organ: [] for organ in organ_names},
        'class_f1': {organ: [] for organ in organ_names},
        'class_support': {organ: [] for organ in organ_names}
    },
    'Random Forest': {
        'accuracy': [], 'f1': [], 'auc_micro': [],
        'class_precision': {organ: [] for organ in organ_names},
        'class_recall': {organ: [] for organ in organ_names},
        'class_f1': {organ: [] for organ in organ_names},
        'class_support': {organ: [] for organ in organ_names}
    },
    'Decision Tree': {
        'accuracy': [], 'f1': [], 'auc_micro': [],
        'class_precision': {organ: [] for organ in organ_names},
        'class_recall': {organ: [] for organ in organ_names},
        'class_f1': {organ: [] for organ in organ_names},
        'class_support': {organ: [] for organ in organ_names}
    },
    'Neural Network': {
        'accuracy': [], 'f1': [], 'auc_micro': [],
        'class_precision': {organ: [] for organ in organ_names},
        'class_recall': {organ: [] for organ in organ_names},
        'class_f1': {organ: [] for organ in organ_names},
        'class_support': {organ: [] for organ in organ_names}
    }
}

# Number of runs
n_runs = 1

for run in range(n_runs):
    print(f"\nRun #{run+1}")
    print("-" * 40)
    
    random_state = 42 + run
    
    # 2. Data splitting
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=random_state
    )
    
    # Binarize labels for multi-class ROC
    y_test_bin = label_binarize(y_test, classes=np.unique(y))
    
    # 3. Create models with Pipeline
    k = min(30, X_train.shape[1])
    
    pipeline_models = [
        ('SVM', Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(f_classif, k=k)),
            ('classifier', SVC(kernel='linear', C=1.0, random_state=random_state, probability=True))
        ])),
        ('Random Forest', Pipeline([
            ('feature_selection', SelectKBest(mutual_info_classif, k=k)),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=random_state))
        ])),
        ('Decision Tree', Pipeline([
            ('feature_selection', SelectKBest(mutual_info_classif, k=k)),
            ('classifier', DecisionTreeClassifier(
                random_state=random_state,
                ccp_alpha=0.01,
                max_depth=10,
                criterion = 'entropy',
                max_features=None, 
                min_samples_leaf=1,
                min_samples_split=2
            ))
        ])),
        ('Neural Network', Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(f_classif, k=k)),
            ('classifier', MLPClassifier(
                hidden_layer_sizes=(50, 25),
                activation='relu',
                solver='adam',
                alpha=0.01,
                batch_size=4,
                learning_rate='adaptive',
                learning_rate_init=0.005,
                max_iter=2000,
                early_stopping=True,
                validation_fraction=0.2,
                n_iter_no_change=150,
                random_state=random_state
            ))
        ]))
    ]
    
    # 4. Evaluate models on test set
    for name, pipeline in pipeline_models:
        try:
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            
            test_accuracy = accuracy_score(y_test, y_pred)
            test_f1 = f1_score(y_test, y_pred, average='macro')
            
            # Calculate per-class metrics
            precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
                y_test, y_pred, labels=np.unique(y), zero_division=0
            )
            
            # Get prediction probabilities for AUC calculation
            if hasattr(pipeline, 'predict_proba'):
                y_score = pipeline.predict_proba(X_test)
            else:
                y_score = pipeline.decision_function(X_test)
                if len(y_score.shape) == 1:
                    y_score = y_score.reshape(-1, 1)
            
            # Calculate micro-average AUC
            fpr_micro, tpr_micro, _ = roc_curve(y_test_bin.ravel(), y_score.ravel())
            auc_micro = auc(fpr_micro, tpr_micro)
            
            # Store results
            all_results[name]['accuracy'].append(test_accuracy)
            all_results[name]['f1'].append(test_f1)
            all_results[name]['auc_micro'].append(auc_micro)
            
            # Store per-class metrics
            for i, organ in enumerate(organ_names):
                all_results[name]['class_precision'][organ].append(precision_per_class[i])
                all_results[name]['class_recall'][organ].append(recall_per_class[i])
                all_results[name]['class_f1'][organ].append(f1_per_class[i])
                all_results[name]['class_support'][organ].append(support_per_class[i])
            
            if run == 0:  # Print detailed results only for first run
                print(f"\n{name}:")
                print(f"  Accuracy: {test_accuracy:.4f}")
                print(f"  F1-score: {test_f1:.4f}")
                print(f"  AUC: {auc_micro:.4f}")
        
        except Exception as e:
            print(f"{name} failed: {e}")
            # Add default values if failed
            all_results[name]['accuracy'].append(0)
            all_results[name]['f1'].append(0)
            all_results[name]['auc_micro'].append(0)
            for organ in organ_names:
                all_results[name]['class_precision'][organ].append(0)
                all_results[name]['class_recall'][organ].append(0)
                all_results[name]['class_f1'][organ].append(0)
                all_results[name]['class_support'][organ].append(0)

# 5. Calculate and output stability results
print("\n" + "="*80)
print("Model Evaluation Results (50 runs)")
print("="*80)

print("\n{:^15} | {:^12} | {:^12} | {:^12} | {:^12} | {:^12} | {:^12}".format(
    "Model", "Avg Acc", "Acc Std", "Avg F1", "F1 Std", "Avg AUC", "AUC Std"))
print("-" * 110)

for name in all_results.keys():
    acc_mean = np.mean(all_results[name]['accuracy'])
    acc_std = np.std(all_results[name]['accuracy'])
    f1_mean = np.mean(all_results[name]['f1'])
    f1_std = np.std(all_results[name]['f1'])
    auc_mean = np.mean(all_results[name]['auc_micro'])
    auc_std = np.std(all_results[name]['auc_micro'])
    
    print("{:^15} | {:^11.4f} | {:^11.4f} | {:^10.4f} | {:^10.4f} | {:^10.4f} | {:^10.4f}".format(
        name, acc_mean, acc_std, f1_mean, f1_std, auc_mean, auc_std))

# Save overall model evaluation results
results_list = []
for name in all_results.keys():
    acc_mean = np.mean(all_results[name]['accuracy'])
    acc_std = np.std(all_results[name]['accuracy'])
    f1_mean = np.mean(all_results[name]['f1'])
    f1_std = np.std(all_results[name]['f1'])
    auc_mean = np.mean(all_results[name]['auc_micro'])
    auc_std = np.std(all_results[name]['auc_micro'])
    
    results_list.append({
        'model': name,
        'avgAcc': acc_mean,
        'Acc_std': acc_std,
        'avgF1': f1_mean,
        'F1_std': f1_std,
        'avgAUC': auc_mean,
        'AUC_std': auc_std
    })

# Convert to DataFrame and save as CSV
df = pd.DataFrame(results_list)
df.to_csv('model_evaluation_results.csv', index=False, float_format='%.4f')
print("Saved to model_evaluation_results.csv")

# 6. Output per-class performance with standard deviations
print("\n" + "="*80)
print("Per-Class Performance (50 runs average with standard deviation)")
print("="*80)

for name in all_results.keys():
    print(f"\n{name} Per-Class Performance (Mean ± Std):")
    print("-" * 80)
    
    # Calculate mean and std for each class
    avg_precision = [np.mean(all_results[name]['class_precision'][organ]) for organ in organ_names]
    std_precision = [np.std(all_results[name]['class_precision'][organ]) for organ in organ_names]
    avg_recall = [np.mean(all_results[name]['class_recall'][organ]) for organ in organ_names]
    std_recall = [np.std(all_results[name]['class_recall'][organ]) for organ in organ_names]
    avg_f1 = [np.mean(all_results[name]['class_f1'][organ]) for organ in organ_names]
    std_f1 = [np.std(all_results[name]['class_f1'][organ]) for organ in organ_names]
    avg_support = [np.mean(all_results[name]['class_support'][organ]) for organ in organ_names]
    
    # Create detailed DataFrame with mean and std
    detailed_df = pd.DataFrame({
        'precision_mean': avg_precision,
        'precision_std': std_precision,
        'recall_mean': avg_recall,
        'recall_std': std_recall,
        'f1_mean': avg_f1,
        'f1_std': std_f1,
        'support_mean': avg_support
    }, index=organ_names)
    
    # Create display DataFrame with mean ± std format
    display_data = []
    for i, organ in enumerate(organ_names):
        display_data.append({
            'Organ': organ,
            'precision': f"{avg_precision[i]:.4f} ± {std_precision[i]:.4f}",
            'recall': f"{avg_recall[i]:.4f} ± {std_recall[i]:.4f}",
            'f1-score': f"{avg_f1[i]:.4f} ± {std_f1[i]:.4f}",
            'support': f"{avg_support[i]:.1f}"
        })
    
    display_df = pd.DataFrame(display_data)
    print(display_df.to_string(index=False))
    
    # Save detailed version to CSV
    detailed_filename = f"per_class_performance_{name.replace(' ', '_')}_detailed.csv"
    detailed_df.to_csv(detailed_filename, float_format='%.4f')
    print(f"Detailed per-class performance saved to: {detailed_filename}")
    
    # Save display version to CSV
    display_filename = f"per_class_performance_{name.replace(' ', '_')}.csv"
    display_df.to_csv(display_filename, index=False)
    print(f"Formatted per-class performance saved to: {display_filename}")

# 7. ROC curves for the last run
print("\n" + "="*80)
print("ROC Curves (Last Run)")
print("="*80)

random_state = 42 + n_runs - 1
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=random_state
)
y_test_bin = label_binarize(y_test, classes=np.unique(y))

roc_data = {}
for name, pipeline in pipeline_models:
    pipeline.fit(X_train, y_train)
    
    if hasattr(pipeline, 'predict_proba'):
        y_score = pipeline.predict_proba(X_test)
    else:
        y_score = pipeline.decision_function(X_test)
        if len(y_score.shape) == 1:
            y_score = y_score.reshape(-1, 1)
    
    roc_data[name] = {
        'y_score': y_score,
        'y_true': y_test,
        'y_true_bin': y_test_bin
    }

# Plot 1-4: Detailed ROC curves for each model (all classes + micro-average)
for model_name in roc_data.keys():
    plt.figure(figsize=(10, 8))
    y_score = roc_data[model_name]['y_score']
    y_true_bin = roc_data[model_name]['y_true_bin']
    
    # Calculate ROC curves and AUC for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
    
    # Calculate micro-average ROC curve
    fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    
    # Plot ROC curves for each class
    colors = plt.cm.rainbow(np.linspace(0, 1, n_classes))
    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=1.5,
                label='{0} (AUC = {1:0.2f})'.format(organ_names[i], roc_auc[i]))
    
    # Plot micro-average ROC curve
    plt.plot(fpr["micro"], tpr["micro"],
            label='Micro-average (AUC = {0:0.2f})'.format(roc_auc["micro"]),
            color='deeppink', linestyle=':', linewidth=4)
    
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curves for {model_name} - All Classes')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save as PDF
    pdf_filename = f"ROC_{model_name.replace(' ', '_')}_All_Classes.pdf"
    plt.savefig(pdf_filename, format='pdf', dpi=300, bbox_inches='tight')
    print(f"Saved: {pdf_filename}")
    
    plt.show()

# Plot 5: Comparison ROC curves for all models (micro-average)
plt.figure(figsize=(10, 8))
colors = ['#4A6FA5', '#C2A5CF', '#45A776', '#E67E22']

for (model_name, color) in zip(roc_data.keys(), colors):
    y_score = roc_data[model_name]['y_score']
    y_true_bin = roc_data[model_name]['y_true_bin']
    
    # Calculate micro-average ROC curve
    fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    roc_auc_micro = auc(fpr_micro, tpr_micro)
    
    plt.plot(fpr_micro, tpr_micro, color=color, lw=2.5,
            label='{0} (AUC = {1:0.2f})'.format(model_name, roc_auc_micro))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves Comparison - All Models (Micro-average)')
plt.legend(loc="lower right")
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save as PDF
pdf_filename = "ROC_All_Models_Comparison.pdf"
plt.savefig(pdf_filename, format='pdf', dpi=300, bbox_inches='tight')
print(f"Saved: {pdf_filename}")

plt.show()

# Export ROC data for the last run
print("\n" + "="*80)
print("ROC Data Export (Last Run)")
print("="*80)

for model_name in roc_data.keys():
    y_score = roc_data[model_name]['y_score']
    y_true_bin = roc_data[model_name]['y_true_bin']
    
    all_fpr = []
    all_tpr = []
    all_classes = []
    all_auc = []
    
    # ROC data for each class
    for i in range(n_classes):
        fpr_i, tpr_i, _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        auc_i = auc(fpr_i, tpr_i)
        
        all_fpr.extend(fpr_i)
        all_tpr.extend(tpr_i)
        all_classes.extend([organ_names[i]] * len(fpr_i))
        all_auc.extend([auc_i] * len(fpr_i))
    
    # Micro-average ROC data
    fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    auc_micro = auc(fpr_micro, tpr_micro)
    
    all_fpr.extend(fpr_micro)
    all_tpr.extend(tpr_micro)
    all_classes.extend(['Micro-average'] * len(fpr_micro))
    all_auc.extend([auc_micro] * len(fpr_micro))
    
    # Create DataFrame and save
    roc_export_df = pd.DataFrame({
        'FPR': all_fpr,
        'TPR': all_tpr,
        'Class': all_classes,
        'AUC': all_auc
    })
    
    filename = f"ROC_Data_{model_name.replace(' ', '_')}.csv"
    roc_export_df.to_csv(filename, index=False)
    print(f"ROC data for {model_name} exported to: {filename}")

print("\nAll operations completed!")
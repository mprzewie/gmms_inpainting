# 2021-05-07 19:03:56.289680
python train_classifier.py --experiment_name=exp_new_classifier_val_size_8/ce_incomp --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/incomplete_data/context_encoder_v1/ --dataset svhn --img_size 32 --mask_train_size 16 --mask_val_size 8 --num_epochs=10 --lr=1e-3 --dump_sample_results --render_every 3 --dataset_root /mnt/remote/wmii_gmum_projects/datasets/vision/SVHN/ --max_benchmark_batches=-1 --convar_type naive

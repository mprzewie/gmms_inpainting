# 2021-04-17 11:59:50.104569
python train_classifier.py --experiment_name=exp_new_classifier_v5/dmfa_fc_frozen_cnv --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/complete_data/dmfa_mse_10_eps/ --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --lr=1e-3 --dump_sample_results --render_every 3 --dataset_root /mnt/remote/wmii_gmum_projects/datasets/vision/SVHN/ --max_benchmark_batches=-1 --convar_type naive

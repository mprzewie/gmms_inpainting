# 2021-04-18 01:47:06.380616
python train_classifier.py --experiment_name=exp_v1/dmfa_fc_incomp --inpainter_type=dmfa --inpainter_path ../results/inpainting/cifar10/fullconv/incomplete_data/dmfa_mse_10_eps_v2/ --dataset cifar10 --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --lr=1e-4 --dump_sample_results --render_every 3 --max_benchmark_batches=-1 --cls_bl 3 --cls_latent_size 256 --cls_dropout=0.5 --cls_depth 3
